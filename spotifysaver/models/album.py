"""Album model for Spotify Saver."""

from dataclasses import dataclass
from typing import List

from .track import Track


@dataclass
class Album:
    """Represents an album and its tracks.
    
    This class encapsulates all information about a music album including
    basic metadata and a collection of tracks.
    
    Attributes:
        name: The name/title of the album
        artists: List of artist names who created the album
        release_date: Release date of the album
        genres: List of genres associated with the album
        cover_url: URL to the album cover art
        tracks: List of Track objects contained in the album
    """

    name: str
    artists: List[str]
    release_date: str
    genres: List[str]
    cover_url: str
    tracks: List[Track]

    def get_track_by_uri(self, uri: str) -> Track | None:
        """Find a track by its Spotify URI.
        
        Args:
            uri: The Spotify URI to search for
            
        Returns:
            Track: The track with matching URI, or None if not found
        """
        return next((t for t in self.tracks if t.uri == uri), None)
