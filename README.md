# SpotifySaver 🎵✨

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-orange?logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-2023.7.6%2B-red)](https://github.com/yt-dlp/yt-dlp)
[![YouTube Music](https://img.shields.io/badge/YouTube_Music-API-yellow)](https://ytmusicapi.readthedocs.io/)
[![Spotify](https://img.shields.io/badge/Spotify-API-1ED760?logo=spotify)](https://developer.spotify.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> All-in-one tool for downloading and organizing music with Spotify metadata for Jellyfin.

The app connects to the Spotify and YouTube Music APIs. The goal is to generate an .nfo XML file to complete the metadata required by Jellyfin when building music libraries.

Read this file in [Spanish](README_ES.md)

## 🌟 Features
- ✅ Download audio from YouTube Music with Spotify metadata
- ✅ Synchronized lyrics (.lrc) from LRC Lib
- 🚧 Generation of Jellyfin-compatible `.info` files
- ✅ Automatic folder structure (Artist/Album)
- ✅ Command-line interface (CLI)

### Requirements
- Python 3.8+
- FFmpeg
- [Spotify Developer Account](https://developer.spotify.com/dashboard/)

```bash
# Installation with Poetry (recommended)
git clone https://github.com/gabrielbaute/spotify-saver.git
cd spotify-saver
poetry install

# Or with pip
pip install git+https://github.com/gabrielbaute/spotify-saver.git
```

⚠️ IMPORTANT: You must log in to your Spotify account as a developer, create an app, and obtain a "client id" and "client secret." You must place this information in an .env file in the project's root directory.

## ⚙️ Configuration

Create `.env` file:

```ini
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret
YTDLP_COOKIES_PATH="cookies.txt" # For age-restricted content
```

The `YTDLP_COOKIES_PATH` variable will indicate the location of the file with the YouTube Music cookies (important, don't use YouTube cookies, but YouTube Music), in case we have problems with restrictions on yt-dlp.

You can also check the .example.env file

## 💻 Using the CLI

### Available Commands

| Command | Description | Example |
|------------------------|--------------------------------------------------|----------------------------------------------|
| `download [URL]` | Download track/album from Spotify | `spotifysaver download "URL_SPOTIFY"` |
| `version` | Displays the installed version | `spotifysaver version` |

### Main Options

| Option | Description | Accepted Values ​​|
|---------------------|------------------------------------------|-------------------------|
| `--lyrics` | Download synchronized lyrics (.lrc) | Flag (no value) |
| `--output DIR` | Output directory | Valid path |
| `--format FORMAT` | Audio format | `m4a` (default), `mp3` |

## 💡 Usage Examples
```bash
# Download album with synchronized lyrics
spotifysaver download "https://open.spotify.com/album/..." --lyrics

# Download song in MP3 format (still in development 🚧)
spotifysaver download "https://open.spotify.com/track/..." --format mp3
```

## 📂 Output Structure
```
Music/
├── Artist/
│ ├── Album (Year)/
│ │ ├── 01 - Song.m4a
│ │ ├── 01 - Song.lrc
│ │ └── cover.jpg
│ └── artist_info.nfo
```

## 🤝 Contributions
1. Fork the project
2. Create your branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add awesome feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## 📄 License

MIT © [TGabriel Baute](https://github.com/gabrielbaute)