# SpotifySaver 🎵✨

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![PyPI Version](https://img.shields.io/pypi/v/spotifysaver?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/spotifysaver/)
[![Docker](https://img.shields.io/badge/Docker-Available-blue?logo=docker&logoColor=white)](https://github.com/gabrielbaute/spotify-saver/pkgs/container/spotify-saver)
[![GitHub Container Registry](https://img.shields.io/badge/ghcr.io-Auto--Build-green?logo=github)](https://github.com/gabrielbaute/spotify-saver/pkgs/container/spotify-saver)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-orange?logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-2023.7.6%2B-red)](https://github.com/yt-dlp/yt-dlp)
[![YouTube Music](https://img.shields.io/badge/YouTube_Music-API-yellow)](https://ytmusicapi.readthedocs.io/)
[![Spotify](https://img.shields.io/badge/Spotify-API-1ED760?logo=spotify)](https://developer.spotify.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/gabrielbaute/spotify-saver)

> ⚠️This repository is under a strong stage of development, expect constant changes. If you find any mistake or bug, please open an ISSUE.

All-in-one tool for downloading and organizing music with Spotify metadata for Jellyfin.

The app connects to the Spotify and YouTube Music APIs. The goal is to generate an .nfo XML file to complete the metadata required by Jellyfin when building music libraries.

Read this file in [Spanish](README_ES.md)

## 🌟 Features
- ✅ Download audio from YouTube Music with Spotify metadata
- ✅ Synchronized lyrics (.lrc) from LRC Lib
- ✅ Generation of Jellyfin-compatible `.info` files (Still some things to work on here! ⚠️)
- ✅ Automatic folder structure (Artist/Album)
- ✅ Command-line interface (CLI)
- ✅ Web interface (UI) with real-time progress
- ✅ RESTful API for integrations
- ✅ Docker support with auto-builds
- ✅ Playlist support
- ✅ MP3 Conversion
- ✅ Support for multiple bitrates (128, 180, 220, etc.)

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

Once in your project directory, run:

```bash
spotifysaver init
```
This will create a local `.env` file with the environment variables that will be requested:

| Variable                  | Description                                | Default Value                     |
|---------------------------|--------------------------------------------|-----------------------------------|
| `SPOTIFY_CLIENT_ID`       | ID of the Spotify app you created          | -                                 |
| `SPOTIFY_CLIENT_SECRET`   | Secret key generated for your Spotify app  | -                                 |
| `SPOTIFY_REDIRECT_URI`    | Spotify API Validation URI                 | `http://localhost:8888/callback`  |
| `SPOTIFYSAVER_OUTPUT_DIR` | Custom directory path (optional)           | `./Music`                         |
| `YTDLP_COOKIES_PATH`      | Cookie file path (optional)                | -                                 |
| `API_PORT`                | API server port (optional)                 | `8000`                            |
| `API_HOST`                | Host for the API (optional)                | `0.0.0.0`                         |
| `UI_ENABLED`              | Enable/disable web interface (optional)    | `true`                            |

The variable `YTDLP_COOKIES_PATH` will indicate the location of the file with the Youtube Music cookies, in case we have problems with restrictions to yt-dlp, specifically it is for cases in which youtube blocks the app for "behaving like a bot" (~~which is not entirely false lol~~)

You can also check the .example.env file

## 📚 Documentation

We maintain a [documentation with Deepwiki](https://deepwiki.com/gabrielbaute/spotify-saver), which constantly tree the repository. You can consult it at all times.

The **documentation for using the API**, on the other hand, can be found in this same repository here: [API Documentation](API_IMPLEMENTATION_SUMMARY.md)

## 💻 Using the CLI

### Available Commands

| Command              | Description                                | Example                                    |
|----------------------|--------------------------------------------|--------------------------------------------|
| `init`               | Configure environment variables            | `spotifysaver init"`                       |
| `download [URL]`     | Download track/album from Spotify          | `spotifysaver download "URL_SPOTIFY"`      |
| `inspect`            | Shows Spotify metadata (album, playlist)   | `spotifysaver inspect "URL_SPOTIFY"`       |
| `show-log`           | Shows the application log                  | `spotifysaver show-log`                    |
| `version`            | Shows the installed version                | `spotifysaver version`                     |

### Download Options

| Option            | Description                                           | Accepted Values         ​​|
|-------------------|-------------------------------------------------------|-------------------------|
| `--lyrics`        | Download synchronized lyrics (.lrc)                   | Flag (no value)         |
| `--output DIR`    | Output directory                                      | Valid path              |
| `--format FORMAT` | Audio format                                          | `m4a` (default), `mp3`  |
| `--cover`         | Saves the cover album in de directoy (.jpg)           | Flag (no value)         |
| `--nfo`           | Generates a .nfo metadata file in the JellyFin format | Flag (no value)         |
| `--explain`       | Show score breakdown for each track without downloading (for error analysis) | Flag (no value)         |
| `--dry-run`       | Simulate download without saving files                | Flag (no value)         |

### show-log Options

| Option      | Description                             | Accepted Values ​​              |
|-------------|-----------------------------------------|-------------------------------|
| `--lines`   | Number of log lines to display          | `--lines 25` --> `int`        |
| `--level`   | Filter by log level                     | INFO, WARNING, DEBUG, ERROR   |
| `--path`    | Displays the location of the log file   | Flag (no value)               |

## 💡 Usage Examples
```bash
# Set spotifysaver configuration
spotifysaver init

# Download album with synchronized lyrics
spotifysaver download "https://open.spotify.com/album/..." --lyrics

# Download album with album cover and metadata file
spotifysaver download "https://open.spotify.com/album/..." --nfo --cover

# Download song in MP3 format
spotifysaver download "https://open.spotify.com/track/..." --format mp3
```

## Usage with API

To use the API, you need to have the API server running. You can start it with the following command:

```bash
# Start the API server
spotifysaver-api
```

The server will run at `http://localhost:8000` by default. You can find the [API documentation here](API_IMPLEMENTATION_SUMMARY.md), which describes the technical aspects and usage in detail.

## 🖥️ Web Interface (UI)

SpotifySaver now includes a modern web interface that makes it easy to download music without using the command line:

```bash
# Start the API server with web interface
spotifysaver-api
```

This will start the API server with an integrated web interface that you can access at `http://localhost:8000`. The web interface provides:

- **Easy URL input**: Simply paste any Spotify URL (track, album, or playlist)
- **Full configuration**: All download options available through an intuitive interface
- **Real-time progress**: Monitor download progress and see detailed logs
- **Responsive design**: Works on desktop and mobile devices
- **Automatic browser opening**: Opens your default browser automatically

### Web Interface Features:
- ✅ URL validation for Spotify links
- ✅ Configurable audio format (M4A/MP3) and bitrate
- ✅ Toggle lyrics and NFO file generation
- ✅ Custom output directory
- ✅ Real-time download progress
- ✅ Activity log with timestamps
- ✅ Error handling and user feedback

**Default Access:**
- Web Interface & API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

## 🐳 Docker Support

SpotifySaver is available as a Docker container with full web interface support. Choose between GitHub Container Registry or building locally.

### 🚀 Quick Start with Docker Compose

1. **Create configuration files:**
```bash
# Create directories
mkdir -p music config

# Create environment file
cat > .env << EOF
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8000/callback
EOF
```

2. **Run with Docker Compose:**
```bash
# Using pre-built image from GitHub Registry
docker compose up -d

# Or build locally
docker compose up --build
```

3. **Access the web interface:**
   - 🌐 **Web UI & API**: http://localhost:8000
   - 📚 **API Docs**: http://localhost:8000/docs

### 📦 Using GitHub Container Registry

**Pull and run directly:**
```bash
# Pull latest version
docker pull ghcr.io/gabrielbaute/spotify-saver:latest

# Run container
docker run -d \
  --name spotifysaver \
  -p 8000:8000 \
  -v ./music:/music \
  -v ./config:/config \
  -e SPOTIFY_CLIENT_ID=your_client_id \
  -e SPOTIFY_CLIENT_SECRET=your_client_secret \
  ghcr.io/gabrielbaute/spotify-saver:latest
```

**Available tags:**
- `latest` - Latest stable release
- `0.6.3-test-2` - Specific version
- `0.6` - Major.minor version

### 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|  
| `SPOTIFY_CLIENT_ID` | Spotify API Client ID | **Required** |
| `SPOTIFY_CLIENT_SECRET` | Spotify API Client Secret | **Required** |
| `SPOTIFY_REDIRECT_URI` | Callback URL | `http://localhost:8000/callback` |
| `API_PORT` | API server port (includes web UI) | `8000` |
| `MUSIC_DIR` | Host music directory | `./music` |
| `CONFIG_DIR` | Host config directory | `./config` |
| `LOG_LEVEL` | Logging level | `INFO` |### 🛠️ Custom Docker Compose Configuration

```yaml
services:
  spotifysaver:
    container_name: spotifysaver
    image: ghcr.io/gabrielbaute/spotify-saver:latest
    ports:
      - "${API_PORT:-8000}:8000"
    environment:
      - SPOTIFY_CLIENT_ID=${SPOTIFY_CLIENT_ID}
      - SPOTIFY_CLIENT_SECRET=${SPOTIFY_CLIENT_SECRET}
      - SPOTIFY_REDIRECT_URI=${SPOTIFY_REDIRECT_URI:-http://localhost:8000/callback}
      - SPOTIFYSAVER_LOG_LEVEL=${LOG_LEVEL:-INFO}
    volumes:
      - ${MUSIC_DIR:-./music}:/music
      - ${CONFIG_DIR:-./config}:/config
      - spotifysaver_logs:/logs
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  spotifysaver_logs:
```

### 🔨 Building Locally

```bash
# Clone repository
git clone https://github.com/gabrielbaute/spotify-saver.git
cd spotify-saver

# Build image
docker build -t spotify-saver .

# Run container
docker run -d \
  --name spotifysaver \
  -p 8000:8000 \
  -v ./music:/music \
  -v ./config:/config \
  -e SPOTIFY_CLIENT_ID=your_client_id \
  -e SPOTIFY_CLIENT_SECRET=your_client_secret \
  spotify-saver
```


## 📂 Output Structure
```
Music/
├── Artist/
│ ├── Album (Year)/
│ │ ├── 01 - Song.m4a
│ │ ├── 01 - Song.lrc
│ │ ├── album.nfo
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
