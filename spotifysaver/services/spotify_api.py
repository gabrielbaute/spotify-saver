"""SpotifyAPI: Interface for interacting with the Spotify Web API."""

from functools import lru_cache
from typing import Dict, List, Optional

import re
import spotipy
from urllib.parse import urlparse
from spotipy.oauth2 import SpotifyClientCredentials

from spotifysaver.config import Config
from spotifysaver.models import Album, Track, Artist, Playlist
from spotifysaver.spotlog import get_logger


class SpotifyAPI:
    """Encapsulated class for interacting with the Spotify API.
    
    This class provides a simplified interface to the Spotify Web API,
    handling authentication and providing methods to retrieve tracks,
    albums, artists, and playlists with proper caching.
    
    Attributes:
        sp: Authenticated Spotipy client instance
    """

    def __init__(self):
        """Initialize the Spotify API client with authentication.
        
        Validates credentials and sets up the authenticated Spotipy client.
        
        Raises:
            ValueError: If Spotify credentials are missing or invalid
        """
        Config.validate()  # Valida las credenciales
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=Config.SPOTIFY_CLIENT_ID,
                client_secret=Config.SPOTIFY_CLIENT_SECRET,
            )
        )
        self.logger = get_logger(f"{self.__class__.__name__}")

    def _extract_spotify_id(self, url: str) -> Optional[str]:
        """
        Extrack the ID from a Spotify URL. It uses regex.

        Args:
            url (str): Spotify URL of a Track, Artist, Album or Playlist
        
        Returns:
            id (Optional[str]): id of the item or None if not found
        """
        pattern = r"(?:track|artist|album|playlist)/([A-Za-z0-9]+)"
        match = re.search(pattern, url)
        return match.group(1) if match else None
    
    def _parse_spotify_url(self, url: str) -> Optional[str]:
        """
        Parse the spotify url and gets the item ID. Uses urlparse from urllib.

        Args:
            url (str): Spotify URL of a Track, Artist, Album or Playlist
        
        Returns:
            id (Optional[str]): id of the item or None if not found        
        """
        path_parts = urlparse(url).path.split("/")
        for i, part in enumerate(path_parts):
            if part in {"track", "artist", "album", "playlist"}:
                return path_parts[i+1] if i+1 < len(path_parts) else None
        return None

    @lru_cache(maxsize=32)
    def _fetch_track_data(self, track_url: str) -> dict:
        """Fetch raw track data from the API.
        
        Args:
            track_url: Spotify URL or URI for the track
            
        Returns:
            dict: Raw track data from Spotify API
            
        Raises:
            ValueError: If track is not found or URL is invalid
        """
        try:
            self.logger.debug(f"Fetching track data: {track_url}")
            track_id = self._extract_spotify_id(track_url)
            if not track_id:
                raise ValueError("Invalid track URL")
            return self.sp.track(track_id)
        except spotipy.exceptions.SpotifyException as e:
            self.logger.error(f"Error fetching track data: {e}")
            raise ValueError("Track not found or invalid URL") from e

    @lru_cache(maxsize=32)  # Cachea las últimas 32 llamadas
    def _fetch_album_data(self, album_url: str) -> dict:
        """Fetch raw album data from the API.
        
        Args:
            album_url: Spotify URL or URI for the album
            
        Returns:
            dict: Raw album data from Spotify API
            
        Raises:
            ValueError: If album is not found or URL is invalid
        """
        try:
            self.logger.info(f"Fetching album data: {album_url}")
            album_id = self._extract_spotify_id(album_url)
            if not album_id:
                raise ValueError("Invalid album URL")
            return self.sp.album(album_id)
        except spotipy.exceptions.SpotifyException as e:
            self.logger.error(f"Error fetching album data: {e}")
            raise ValueError("Album not found or invalid URL") from e

    @lru_cache(maxsize=32)
    def _fetch_artist_data(self, artist_url: str) -> dict:
        """Fetch raw artist data from the API.
        
        Args:
            artist_url: Spotify URL or URI for the artist
            
        Returns:
            dict: Raw artist data from Spotify API
            
        Raises:
            ValueError: If artist is not found or URL is invalid
        """
        try:
            self.logger.debug(f"Fetching artist data: {artist_url}")
            artist_id = self._extract_spotify_id(artist_url)
            if not artist_id:
                raise ValueError("Invalid artist URL")
            return self.sp.artist(artist_id)
        except spotipy.exceptions.SpotifyException as e:
            self.logger.error(f"Error fetching artist data: {e}")
            raise ValueError("Artist not found or invalid URL") from e

    @lru_cache(maxsize=32)
    def _fetch_playlist_data(self, playlist_url: str) -> dict:
        """Fetch raw playlist data from the API.
        
        Args:
            playlist_url: Spotify URL or URI for the playlist
            
        Returns:
            dict: Raw playlist data from Spotify API
            
        Raises:
            ValueError: If playlist is not found or URL is invalid
        """
        try:
            self.logger.info(f"Fetching playlist data: {playlist_url}")
            playlist_id = self._extract_spotify_id(playlist_url)
            if not playlist_id:
                raise ValueError("Invalid playlist URL")
            return self.sp.playlist(playlist_id)
        except spotipy.exceptions.SpotifyException as e:
            self.logger.error(f"Error fetching playlist data: {e}")
            raise ValueError("Playlist not found or invalid URL") from e

    @lru_cache(maxsize=32)
    def fetch_artist_albums(self, artist_url: str) -> dict:
        """Fetch raw artist data from the API.
        
        Args:
            artist_url: Spotify URL or URI for the artist
            
        Returns:
            dict: Raw artist data from Spotify API
            
        Raises:
            ValueError: If artist is not found or URL is invalid
        """
        try:
            self.logger.debug(f"Fetching artist albums: {artist_url}")
            artist_id = self._extract_spotify_id(artist_url)
            if not artist_id:
                raise ValueError("Invalid artist URL")
            return self.sp.artist_albums(artist_id)
        except spotipy.exceptions.SpotifyException as e:
            self.logger.error(f"Error fetching artist albuns: {e}")
            raise ValueError("Artist not found or invalid URL") from e

    def get_track(self, track_url: str) -> Track:
        """Get an individual track (for singles or specific searches).
        
        Args:
            track_url: Spotify URL or URI for the track
            
        Returns:
            Track: Track object with complete metadata
            
        Raises:
            ValueError: If track is not found
        """
        raw_data = self._fetch_track_data(track_url)
        if not raw_data:
            self.logger.error(f"Track not found: {track_url}")
            raise ValueError("Track not found")

        return Track(
            number=raw_data["track_number"],
            total_tracks=1,  # Individual tracks have total_tracks = 1
            name=raw_data["name"],
            duration=raw_data["duration_ms"] // 1000,
            uri=raw_data["uri"],
            artists=[a["name"] for a in raw_data["artists"]],
            album_artist=[a["name"] for a in raw_data["album"]["artists"]],
            album_name=raw_data["album"]["name"] if raw_data["album"] else None,
            release_date=(
                raw_data["album"]["release_date"] if raw_data["album"] else "NA"
            ),
            cover_url=(
                raw_data["album"]["images"][0]["url"]
                if raw_data["album"]["images"]
                else None
            ),
        )

    def get_album(self, album_url: str) -> Album:
        """Get an Album object with its tracks.
        
        Args:
            album_url: Spotify URL or URI for the album
            
        Returns:
            Album: Album object with complete metadata and track list
        """
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
                album_artist=[a["name"] for a in raw_data["artists"]],
                genres=raw_data.get("genres", []),
                album_name=raw_data["name"],
                release_date=raw_data["release_date"],
                disc_number=track.get("disc_number", 1),
                cover_url=raw_data["images"][0]["url"] if raw_data["images"] else None,
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
            tracks=tracks,
        )

    def get_artist(self, artist_url: str) -> Dict[str, Optional[str]]:
        """Get basic artist information.
        
        Args:
            artist_url: Spotify URL or URI for the artist
            
        Returns:
            Artist: Artist object with metadata
            
        Raises:
            ValueError: If artist is not found
        """
        raw_data = self._fetch_artist_data(artist_url)
        if not raw_data:
            self.logger.error(f"Artist not found: {artist_url}")
            raise ValueError("Artist not found")

        return Artist(
            name=raw_data["name"],
            uri=raw_data["uri"],
            cover=raw_data.get("images", ["url"]),
            genres=raw_data.get("genres", []),
            popularity=raw_data["popularity"],
            followers=raw_data["followers"]["total"],
            image_url=raw_data["images"][0]["url"] if raw_data["images"] else None,
        )

    def get_playlist(self, playlist_url: str) -> Playlist:
        """Get a Playlist object with its tracks.
        
        Args:
            playlist_url: Spotify URL or URI for the playlist
            
        Returns:
            Playlist: Playlist object with complete metadata and track list
        """
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
                album_artist=[a["name"] for a in track["track"]["album"]["artists"]],
                album_name=(
                    track["track"]["album"]["name"] if track["track"]["album"] else None
                ),
                release_date=(
                    track["track"]["album"]["release_date"]
                    if track["track"]["album"]
                    else "NA"
                ),
                cover_url=(
                    track["track"]["album"]["images"][0]["url"]
                    if track["track"]["album"]["images"]
                    else None
                ),
            )
            for idx, track in enumerate(raw_data["tracks"]["items"])
            if track["track"]
        ]

        return Playlist(
            name=raw_data["name"],
            description=raw_data.get("description", ""),
            owner=raw_data["owner"]["display_name"],
            uri=raw_data["uri"],
            cover_url=raw_data["images"][0]["url"] if raw_data["images"] else None,
            tracks=tracks,
        )
