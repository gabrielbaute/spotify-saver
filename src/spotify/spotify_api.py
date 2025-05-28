import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from functools import lru_cache
from typing import Dict, List, Optional

from src.config import Config
from src.spotify.models.album import Album
from src.spotify.models.track import Track
from src.spotlog.logger import get_logger

logger = get_logger("SpotifyAPI")

class SpotifyAPI:
    """Clase encapsulada para interactuar con la API de Spotify."""
    
    def __init__(self):
        Config.validate()  # Valida las credenciales
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=Config.SPOTIFY_CLIENT_ID,
            client_secret=Config.SPOTIFY_CLIENT_SECRET,
        ))
    
    @lru_cache(maxsize=32)  # Cachea las últimas 32 llamadas
    def _fetch_album_data(self, album_url: str) -> dict:
        """Obtiene datos crudos del álbum desde la API."""
        logger.debug(f"Fetching album data: {album_url}")
        return self.sp.album(album_url)

    def get_album(self, album_url: str) -> Album:
        """Devuelve un objeto Album con sus tracks."""
        raw_data = self._fetch_album_data(album_url)
        
        # Construye objetos Track
        tracks = [
            Track(
                number=track["track_number"],
                name=track["name"],
                duration=track["duration_ms"] // 1000,
                uri=track["uri"],
                artists=[a["name"] for a in track["artists"]],
                album_name=raw_data["name"],
                cover_url=raw_data["images"][0]["url"] if raw_data["images"] else None
            )
            for track in raw_data["tracks"]["items"]
        ]

        # Construye objeto Album
        return Album(
            name=raw_data["name"],
            artists=[a["name"] for a in raw_data["artists"]],
            release_date=raw_data["release_date"],
            genres=raw_data.get("genres", []),
            cover_url=raw_data["images"][0]["url"] if raw_data["images"] else None,
            tracks=tracks
        )