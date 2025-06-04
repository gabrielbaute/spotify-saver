"""LRC Lib API Client."""

from typing import Optional, Dict

import requests

from spotifysaver.models import Track
from spotifysaver.spotlog import get_logger
from spotifysaver.services.errors.errors import APIError

logger = get_logger("LrclibAPI")


class LrclibAPI:
    """LRC Lib API client for fetching synchronized lyrics.
    
    This class provides an interface to the LRC Lib API for retrieving
    synchronized and plain lyrics for music tracks.
    
    Attributes:
        BASE_URL: Base URL for the LRC Lib API
        session: HTTP session for making requests    """
    
    BASE_URL = "https://lrclib.net/api"

    def __init__(self):
        """Initialize the LRC Lib API client.
        
        Sets up the HTTP session with appropriate timeout settings.
        """
        self.session = requests.Session()
        self.session.timeout = 10  # 10 seconds timeout

    def get_lyrics(self, track: Track, synced: bool = True) -> Optional[str]:
        """Get synchronized or plain lyrics for a track.

        Args:
            track: Track object with metadata for lyrics search
            synced: If True, returns synchronized lyrics (.lrc format)

        Returns:
            str: Lyrics in requested format, or None if not found/error occurred
            
        Raises:
            APIError: If there's an error with the API request
        """
        try:
            params = {
                "track_name": track.name,
                "artist_name": track.artists[0],
                "album_name": track.album_name,
                "duration": int(track.duration),
            }

            response = self.session.get(
                f"{self.BASE_URL}/get",
                params=params,
                headers={"Accept": "application/json"},
            )

            if response.status_code == 404:
                logger.debug(f"Lyrics not found for: {track.name}")
                return None

            response.raise_for_status()
            data = response.json()

            lyric_type = "syncedLyrics" if synced else "plainLyrics"
            logger.info(f"Song lyrics obtained: {lyric_type}")
            return data.get(lyric_type)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error in the LRC Lib API: {str(e)}")
            raise APIError(f"LRC Lib API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise APIError(f"Unexpected error: {str(e)}")

    def get_lyrics_with_fallback(self, track: Track) -> Optional[str]:
        """Attempt to get synchronized lyrics, fallback to plain lyrics if failed.
        
        Args:
            track: Track object with metadata for lyrics search
            
        Returns:
            str: Lyrics (synchronized preferred, plain as fallback), or None if unavailable
        """
        try:
            return self.get_lyrics(track, synced=True) or self.get_lyrics(
                track, synced=False
            )
        except APIError:
            return None
