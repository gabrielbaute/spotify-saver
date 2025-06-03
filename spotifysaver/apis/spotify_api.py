import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from functools import lru_cache
from typing import Dict, List, Optional

from spotifysaver.config import Config
from spotifysaver.models import Album, Track, Artist, Playlist
from spotifysaver.spotlog import get_logger

logger = get_logger("SpotifyAPI")

class SpotifyAPI:
    """Clase encapsulada para interactuar con la API de Spotify."""
    
    def __init__(self):
        Config.validate()  # Valida las credenciales
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=Config.SPOTIFY_CLIENT_ID,
            client_secret=Config.SPOTIFY_CLIENT_SECRET,
        ))

    @lru_cache(maxsize=32)
    def _fetch_track_data(self, track_url: str) -> dict:
        """Obtiene datos crudos del track desde la API."""
        try:
            logger.debug(f"Fetching track data: {track_url}")
            return self.sp.track(track_url)
        except spotipy.exceptions.SpotifyException as e:
            logger.error(f"Error fetching track data: {e}")
            raise ValueError("Track not found or invalid URL") from e

    @lru_cache(maxsize=32)  # Cachea las últimas 32 llamadas
    def _fetch_album_data(self, album_url: str) -> dict:
        """Obtiene datos crudos del álbum desde la API."""
        try:
            logger.info(f"Fetching album data: {album_url}")
            return self.sp.album(album_url)
        except spotipy.exceptions.SpotifyException as e:
            logger.error(f"Error fetching album data: {e}")
            raise ValueError("Album not found or invalid URL") from e
    
    @lru_cache(maxsize=32)
    def _fetch_artist_data(self, artist_url: str) -> dict:
        """Obtiene datos crudos del artista desde la API."""
        try:
            logger.debug(f"Fetching artist data: {artist_url}")
            return self.sp.artist(artist_url)
        except spotipy.exceptions.SpotifyException as e:
            logger.error(f"Error fetching artist data: {e}")
            raise ValueError("Artist not found or invalid URL") from e

    @lru_cache(maxsize=32)
    def _fetch_playlist_data(self, playlist_url: str) -> dict:
        """Obtiene datos crudos de la playlist desde la API."""
        try:
            logger.info(f"Fetching playlist data: {playlist_url}")
            return self.sp.playlist(playlist_url)
        except spotipy.exceptions.SpotifyException as e:
            logger.error(f"Error fetching playlist data: {e}")
            raise ValueError("Playlist not found or invalid URL") from e

    def get_track(self, track_url: str) -> Track:
        """Obtiene un track individual (para singles o búsquedas específicas)."""
        raw_data = self._fetch_track_data(track_url)
        if not raw_data:
            logger.error(f"Track not found: {track_url}")
            raise ValueError("Track not found")
        
        return Track(
            number=raw_data["track_number"],
            name=raw_data["name"],
            duration=raw_data["duration_ms"] // 1000,
            uri=raw_data["uri"],
            artists=[a["name"] for a in raw_data["artists"]],
            album_name=raw_data["album"]["name"] if raw_data["album"] else None,
            release_date=raw_data["album"]["release_date"] if raw_data["album"] else "NA",
            cover_url=raw_data["album"]["images"][0]["url"] if raw_data["album"]["images"] else None
        )

    def get_album(self, album_url: str) -> Album:
        """Devuelve un objeto Album con sus tracks."""
        raw_data = self._fetch_album_data(album_url)
        
        # Construye objetos Track
        tracks = [
            Track(
                source_type="album",
                number=track["track_number"],
                total_tracks=raw_data["total_tracks"],
                name=track["name"],
                duration=track["duration_ms"] // 1000,
                uri=track["uri"],
                artists=[a["name"] for a in track["artists"]],
                genres=raw_data.get("genres", []),
                album_name=raw_data["name"],
                release_date=raw_data["release_date"],
                disc_number=track.get("disc_number", 1),
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

    def get_artist(self, artist_url: str) -> Dict[str, Optional[str]]:
        """Obtiene información básica de un artista."""
        raw_data = self._fetch_artist_data(artist_url)
        if not raw_data:
            logger.error(f"Artist not found: {artist_url}")
            raise ValueError("Artist not found")
        
        return Artist(
            name=raw_data["name"],
            uri=raw_data["uri"],
            genres=raw_data.get("genres", []),
            popularity=raw_data["popularity"],
            followers=raw_data["followers"]["total"],
            image_url=raw_data["images"][0]["url"] if raw_data["images"] else None
        )

    def get_playlist(self, playlist_url: str) -> Playlist:
        """Devuelve un objeto Playlist con sus tracks."""
        raw_data = self._fetch_playlist_data(playlist_url)
        
        tracks = [
            Track(
                source_type="playlist",
                playlist_name=raw_data["name"],
                number=idx + 1,
                total_tracks=raw_data["tracks"]["total"],
                name=track["track"]["name"],
                duration=track["track"]["duration_ms"] // 1000,
                uri=track["track"]["uri"],
                artists=[a["name"] for a in track["track"]["artists"]],
                album_name=track["track"]["album"]["name"] if track["track"]["album"] else None,
                release_date=track["track"]["album"]["release_date"] if track["track"]["album"] else "NA",
                cover_url=track["track"]["album"]["images"][0]["url"] if track["track"]["album"]["images"] else None
            )
            for idx, track in enumerate(raw_data["tracks"]["items"])
            if track["track"]
        ]

        # Construye objeto Playlist
        return Playlist(
            name=raw_data["name"],
            description=raw_data.get("description", ""),
            owner=raw_data["owner"]["display_name"],
            uri=raw_data["uri"],
            cover_url=raw_data["images"][0]["url"] if raw_data["images"] else None,
            tracks=tracks
        )