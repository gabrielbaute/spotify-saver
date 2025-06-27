"""SpotifySaver - Download Music from Spotify via YouTube Music.

SpotifySaver is a comprehensive tool that allows users to download music from Spotify
by finding equivalent tracks on YouTube Music. It preserves metadata, fetches lyrics,
and organizes files in a structured manner compatible with media servers like Jellyfin.

Features:
- Download individual tracks, albums, and playlists from Spotify
- Intelligent YouTube Music search with multiple matching strategies
- Metadata preservation including artist, album, track info, and cover art
- Lyrics fetching from LRCLib with synchronized timestamps
- NFO file generation for media server compatibility
- Organized file structure with proper naming conventions
- Progress tracking and comprehensive logging
- CLI interface with detailed inspection capabilities

The application uses the Spotify Web API to fetch metadata and YouTube Music
to source the actual audio files, ensuring high-quality downloads with complete
metadata preservation.
"""

__version__ = "0.4.2"


# Verify if ffmpeg is installed
import subprocess


def check_ffmpeg_installed():
    """Check if ffmpeg is installed on the system."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
        return True
    except FileNotFoundError:
        return False


if not check_ffmpeg_installed():
    raise EnvironmentError(
        "ffmpeg is not installed. Please install ffmpeg to use SpotifySaver."
    )
