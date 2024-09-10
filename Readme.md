# Spotify Playlist Generator

## Overview

The **Spotify Playlist Generator** is a Python script that interacts with the Spotify API to create and manage playlists based on user-provided song lists. The application allows you to:
- Create or update a Spotify playlist.
- Optionally add song recommendations based on the provided songs.
- Export the playlist to a text file.
- Customize the maximum duration of songs to be added.

## Features

- **Create or Update Playlist:** Automatically creates a new playlist or updates an existing one.
- **Add Recommendations:** Optionally add recommended songs based on the initial songs provided.
- **Export Playlist:** Export the current playlist to a text file.
- **Custom Duration:** Easily set the maximum song duration via the `songs.txt` file.
- **Warning for Long Songs:** Alerts for songs longer than the specified duration.

## Prerequisites

- Python 3.6 or later
- Spotify Developer Account (for API access)

## Installation

1. **Clone the Repository:**

  ```bash
  git clone https://github.com/bashbang/spotify-playlist-generator.git
  cd spotify-playlist-generator
  ```

1. **Set Up a Virtual Environment:**

   ```bash
    python -m venv venv
    source venv/bin/activate
  ```

1. **Install Dependencies:**

  ```bash
  pip install -r requirements.txt
  ```

1. **Set Up Spotify API Credentials:**
  - Create a file named config.json in the root directory with the following content:

  ```json
    {
      "client_id": "YOUR_SPOTIFY_CLIENT_ID",
      "client_secret": "YOUR_SPOTIFY_CLIENT_SECRET",
      "redirect_uri": "YOUR_SPOTIFY_REDIRECT_URI"
    }
  ```

## Usage
- Create or Update a Playlist from list in songs.txt:
  ```bash
  python main.py
  ```

- Create or Update a Playlist with Recommendations:
  ```bash
  python main.py --recommendations
  ```

- Export the Playlist to songs.txt:
  ```bash
  python main.py --export
  ```

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing
Feel free to contribute by submitting issues or pull requests. Please follow the code of conduct and guidelines provided in the CONTRIBUTING.md file.

## Contact
For any questions or feedback, please reach out in [issues](https://github.com/bashbang/spotify-playlist-generator/issues).
