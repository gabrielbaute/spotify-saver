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
        try:
            logger.debug(f"Fetching album data: {album_url}")
            return self.sp.album(album_url)
        except spotipy.exceptions.SpotifyException as e:
            logger.error(f"Error fetching album data: {e}")
            raise ValueError("Album not found or invalid URL") from e

    @lru_cache(maxsize=32)
    def _fetch_track_data(self, track_url: str) -> dict:
        """Obtiene datos crudos del track desde la API."""
        try:
            logger.debug(f"Fetching track data: {track_url}")
            return self.sp.track(track_url)
        except spotipy.exceptions.SpotifyException as e:
            logger.error(f"Error fetching track data: {e}")
            raise ValueError("Track not found or invalid URL") from e
    
    @lru_cache(maxsize=32)
    def _fetch_artist_data(self, artist_url: str) -> dict:
        """Obtiene datos crudos del artista desde la API."""
        try:
            logger.debug(f"Fetching artist data: {artist_url}")
            return self.sp.artist(artist_url)
        except spotipy.exceptions.SpotifyException as e:
            logger.error(f"Error fetching artist data: {e}")
            raise ValueError("Artist not found or invalid URL") from e

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

    def get_track(self, track_url: str) -> Track:
        """Obtiene un track individual (para singles o búsquedas específicas)."""
        raw_data = self._fetch_track_data(track_url)
        if not raw_data:
            logger.error(f"Track not found: {track_url}")
            raise ValueError("Track not found")
        
        return Track(
            number=1,  # Los singles suelen ser track 1
            name=raw_data["name"],
            duration=raw_data["duration_ms"] // 1000,
            uri=raw_data["uri"],
            artists=[a["name"] for a in raw_data["artists"]],
            cover_url=raw_data["album"]["images"][0]["url"] if raw_data["album"]["images"] else None
        )
    
    def get_artist(self, artist_url: str) -> Dict[str, Optional[str]]:
        """Obtiene información básica de un artista."""
        raw_data = self._fetch_artist_data(artist_url)
        if not raw_data:
            logger.error(f"Artist not found: {artist_url}")
            raise ValueError("Artist not found")
        
        return {
            "name": raw_data["name"],
            "genres": raw_data.get("genres", []),
            "followers": raw_data["followers"]["total"],
            "popularity": raw_data["popularity"],
            "uri": raw_data["uri"],
            "image_url": raw_data["images"][0]["url"] if raw_data["images"] else None
        }
