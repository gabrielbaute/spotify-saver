"""Playlist model for Spotify Saver."""

from dataclasses import dataclass
from typing import List

from .track import Track


@dataclass
class Playlist:
    """Represents a Spotify playlist and its tracks.
    
    This class encapsulates all information about a playlist including
    metadata and the collection of tracks it contains.
    
    Attributes:
        name: The playlist name/title
        description: Description or summary of the playlist
        owner: Username of the playlist owner
        uri: Spotify URI for the playlist
        cover_url: URL to the playlist cover image
        tracks: List of Track objects in the playlist
    """

    name: str
    description: str
    owner: str
    uri: str
    cover_url: str
    tracks: List[Track]

    def get_track_by_uri(self, uri: str) -> Track | None:
        """Find a track by its URI (similar to Album method).
        
        Args:
            uri: The Spotify URI to search for
            
        Returns:
            Track: The track with matching URI, or None if not found
        """
        return next((t for t in self.tracks if t.uri == uri), None)
