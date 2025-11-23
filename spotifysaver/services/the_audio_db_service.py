import requests
from typing import Optional, Dict, Any, List

from spotifysaver.spotlog import get_logger
from spotifysaver.services.audiodb_parser import AudioDBParser
from spotifysaver.services.schemas import TrackADBResponse, AlbumADBResponse, ArtistADBResponse

class TheAudioDBService():
    """
    Search for metadata in TheAudioDB.

    This class provides methods to obtain metadata for artist, albums and tracks from TheAudioDB.
    """
    def __init__(self):
        self.logger = get_logger(f"{__class__.__name__}")
        self.url_base = "https://www.theaudiodb.com/api/v1/json/123/"
        self.parser = AudioDBParser()

    def _search_artist_by_name(self, artist_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for an artist by name.

        Args:
            artist_name (str): The name of the artist to search for.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the artist information if found, otherwise None.
        """
        self.logger.info(f"Searching artist by name: {artist_name}")
        try:
            response = requests.get(f"{self.url_base}search.php?s={artist_name}")
            if response.status_code == 200:
                raw = response.json()
                artists = raw.get("artists")
                if artists and isinstance(artists, list) and len(artists) > 0:
                    return artists[0]
                else:
                    self.logger.warning(f"No artist found for {artist_name}")
                    return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error: {e}")
            return None
    
    def _search_album_by_name(self, artist_name: str, album_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for an album by name and artist.

        Args:
            artist_name (str): The name of the artist.
            album_name (str): The name of the album.
        
        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the album information if found, otherwise None.
        """
        self.logger.info(f"Searching album by name: {album_name}")
        try:
            response = requests.get(f"{self.url_base}searchalbum.php?s={artist_name}&a={album_name}")
            if response.status_code == 200:
                raw = response.json()
                albums = raw.get("album")
                if albums and isinstance(albums, list) and len(albums) > 0:
                    return albums[0]
                else:
                    self.logger.warning(f"No album found for {artist_name} - {album_name}")
                    return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error: {e}")
            return None
    
    def _search_track_by_name(self, artist_name: str, track_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for a track by name and artist.

        Args:
            artist_name (str): The name of the artist.
            track_name (str): The name of the track.
        
        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the track information if found, otherwise None.
        """
        self.logger.info(f"Searching track by name: {track_name}")
        try:
            response = requests.get(f"{self.url_base}searchtrack.php?s={artist_name}&t={track_name}")
            if response.status_code == 200:
                raw = response.json()
                tracks = raw.get("track")
                if tracks and isinstance(tracks, list) and len(tracks) > 0:
                    return tracks[0]
                else:
                    self.logger.warning(f"No track found for {artist_name} - {track_name}")
                    return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error: {e}")
            return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error: {e}")
            return None

    def _get_tracks_from_an_album(self, album_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get tracks from an album.

        Args:
            album_id (str): The ID of the album.
        
        Returns:
            Optional[List[Dict[str, Any]]]: A dictionary containing the tracks information if found, otherwise None.
        """
        self.logger.info(f"Getting tracks from album: {album_id}")
        try:
            response = requests.get(f"{self.url_base}track.php?m={album_id}")
            if response.status_code == 200:
                raw = response.json()
                tracks = raw.get("track")
                if tracks and isinstance(tracks, list) and len(tracks) > 0:
                    return tracks
                else:
                    self.logger.warning(f"No tracks found for album: {album_id}")
                    return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error: {e}")
            return None

    def _search_track_by_id(self, track_id: str) -> Optional[Dict[str, Any]]:
        """
        Search for a track by ID.

        Args:
            track_id (str): The ID of the track.
        
        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the track information if found, otherwise None.
        """
        self.logger.info(f"Searching track by ID: {track_id}")
        try:
            response = requests.get(f"{self.url_base}track.php?i={track_id}")
            if response.status_code == 200:
                raw = response.json()
                tracks = raw.get("track")
                if tracks and isinstance(tracks, list) and len(tracks) > 0:
                    return tracks[0]
                else:
                    self.logger.warning(f"No track found for ID: {track_id}")
                    return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error: {e}")
            return None
        
    def get_track_metadata(
            self, 
            track_name: str, 
            artist_name: Optional[str] = None, 
        ) -> TrackADBResponse:
        """
        Get the metadata of a track.

        Args:
            track_name (str): The name of the track.
            artist_name (Optional[str]): The name of the artist.
            album_name (Optional[str]): The name of the album.
        
        Returns:
            TrackADBResponse: A dictionary containing the track metadata.
        """
        raw_data = self._search_track_by_name(artist_name, track_name)
        if not raw_data:
            return None

        return self.parser.parse_track(raw_data)
    
    def get_album_metadata(
            self, 
            artist_name: str, 
            album_name: str, 
        ) -> AlbumADBResponse:
        """
        Get the metadata of an album.

        Args:
            artist_name (str): The name of the artist
            album_name (str): The name of the album.
        
        Returns:
            AlbumADBResponse: A dictionary containing the album metadata.
        """
        raw_data = self._search_album_by_name(artist_name, album_name)
        if not raw_data:
            return None

        return self.parser.parse_album(raw_data)

    def get_artist_metadata(
            self, 
            artist_name: str, 
        ) -> ArtistADBResponse:
        """
        Get the metadata of an artist.

        Args:
            artist_name (str): The name of the artist.
        
        Returns:
            ArtistADBResponse: A dictionary containing the artist metadata.
        """
        raw_data = self._search_artist_by_name(artist_name)
        if not raw_data:
            return None

        return self.parser.parse_artist(raw_data)