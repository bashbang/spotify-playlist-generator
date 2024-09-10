import spotipy
from spotipy.oauth2 import SpotifyOAuth
import argparse
import json
import re

# Load configuration from an external file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

CLIENT_ID = config['client_id']
CLIENT_SECRET = config['client_secret']
REDIRECT_URI = config['redirect_uri']

# Authentication
scope = 'playlist-modify-public playlist-modify-private user-top-read'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=scope))

# Load playlist configuration from a separate file.
def load_playlist_config(filename):
    playlist_name = None
    playlist_description = None
    max_duration = 5  # Default max duration in minutes

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("Playlist Name:"):
                playlist_name = line[len("Playlist Name:"):].strip()
            elif line.startswith("Playlist Description:"):
                playlist_description = line[len("Playlist Description:"):].strip()
            elif line.startswith("Max Duration:"):
                try:
                    max_duration = int(line[len("Max Duration:"):].strip())
                except ValueError:
                    print(f"Warning: Invalid duration value '{line[len('Max Duration:'):]}'")

    if not playlist_name or not playlist_description:
        raise ValueError("The configuration file is missing required information.")

    return playlist_name, playlist_description, max_duration

# Load songs from a separate file.
def load_songs(filename):
    songs = []
    correct_pattern = re.compile(r'^.+ - .+$')

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                if correct_pattern.match(line):
                    song_title, artist = line.split(' - ', 1)
                    if not is_valid_song_title_and_artist(song_title, artist):
                        print(f"Warning: The entry '{line}' appears to have inverted song title and artist.")
                    songs.append(line)
                else:
                    print(f"Warning: The entry '{line}' does not match the expected format 'Song Title - Artist Name'.")
    return songs

def is_valid_song_title_and_artist(song_title, artist):
    if len(song_title) < 3 or len(artist) < 3:
        return False
    return True

# Search for the user's playlists to find the one we want to update
def get_playlist_by_name(playlist_name):
    playlists = sp.current_user_playlists(limit=50)
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            return playlist
    return None

# Get all the track URIs from the playlist and remove them
def clear_playlist(playlist_id):
    tracks = sp.playlist_tracks(playlist_id)
    track_uris = [item['track']['uri'] for item in tracks['items']]
    if track_uris:
        sp.playlist_remove_all_occurrences_of_items(playlist_id, track_uris)

# Search for a song and return the track ID if found.
def get_track_id(sp, song, max_duration):
    results = sp.search(q=song, type='track', limit=1)
    tracks = results['tracks']['items']
    if len(tracks) > 0:
        track = tracks[0]
        duration_minutes = track['duration_ms'] / 60000  # Convert milliseconds to minutes
        if duration_minutes > max_duration:
            print(f"Warning: The song '{track['name']}' by '{track['artists'][0]['name']}' is longer than the allowed duration of {max_duration} minutes. Duration: {duration_minutes:.2f} minutes.")
        return track['id']
    return None

# Get song recommendations based on a track ID, and filter out songs longer than max_duration minutes.
def get_recommendations(sp, track_id, max_duration):
    recommended_ids = []
    rec_results = sp.recommendations(seed_tracks=[track_id], limit=2)
    for rec in rec_results['tracks']:
        duration_minutes = rec['duration_ms'] / 60000  # Convert milliseconds to minutes
        if duration_minutes <= max_duration:
            recommended_ids.append(rec['id'])
        else:
            print(f"Warning: Recommended song '{rec['name']}' by '{rec['artists'][0]['name']}' is longer than the allowed duration of {max_duration} minutes. Duration: {duration_minutes:.2f} minutes.")
    return recommended_ids

# Add tracks to the specified playlist.
def add_tracks_to_playlist(sp, playlist_id, track_ids):
    if track_ids:
        sp.playlist_add_items(playlist_id, track_ids)

# Main function to add songs and optionally their recommendations to the playlist.
def add_songs_to_playlist(sp, playlist_id, songs, add_recommendations, max_duration):
    track_ids = []

    for song in songs:
        track_id = get_track_id(sp, song, max_duration)
        if track_id:
            track_ids.append(track_id)
            if add_recommendations:
                track_ids.extend(get_recommendations(sp, track_id, max_duration))

    add_tracks_to_playlist(sp, playlist_id, track_ids)

# Export the playlist to a file.
def export_playlist_to_file(playlist_id, filename):
    tracks = sp.playlist_tracks(playlist_id)
    with open(filename, 'w') as file:
        for item in tracks['items']:
            track = item['track']
            file.write(f"{track['name']} - {track['artists'][0]['name']}\n")
    print(f"Playlist exported to {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create or update a Spotify playlist and optionally add recommended songs.")
    parser.add_argument('--recommendations', action='store_true', help='Add recommended songs to the playlist')
    parser.add_argument('--export', action='store_true', help='Export the playlist to songs.txt')
    args = parser.parse_args()

    try:
        playlist_name, playlist_description, max_duration = load_playlist_config('playlist_config.txt')
        songs = load_songs('songs.txt')
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)

    # Get the current user
    user_id = sp.me()['id']

    # Check if the playlist already exists
    existing_playlist = get_playlist_by_name(playlist_name)

    if existing_playlist:
        print(f"Found existing playlist: {existing_playlist['name']}.")
        playlist_id = existing_playlist['id']
    else:
        print(f"Creating new playlist: {playlist_name}")
        # Create a new playlist
        playlist = sp.user_playlist_create(user_id, playlist_name, public=True, description=playlist_description)
        playlist_id = playlist['id']

    # Export the playlist if the --export flag is provided
    if args.export:
        export_playlist_to_file(playlist_id, 'songs.txt')
    else:
        # Clear the existing playlist and add songs
        clear_playlist(playlist_id)
        add_songs_to_playlist(sp, playlist_id, songs, args.recommendations, max_duration)
        print(f"Playlist '{playlist_name}' updated successfully with recommendations={args.recommendations}!")
