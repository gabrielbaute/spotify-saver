"""Artist model for Spotify Saver."""

from dataclasses import dataclass
from typing import List


@dataclass
class Artist:
    """Represents an individual artist with metadata.
    
    This class encapsulates all information about a music artist including
    basic information and statistics.
    
    Attributes:
        name: The artist's name
        uri: Spotify URI for the artist
        genres: List of genres associated with the artist
        image_url: URL to the artist's profile image
    """

    name: str
    uri: str
    cover: str
    genres: List[str] = None
    image_url: str = None

    def to_dict(self) -> dict:
        """Convert the artist object to a dictionary for serialization.

        Returns:
            dict: Dictionary representation of the artist with all metadata
        """
        return {
            "name": self.name,
            "uri": self.uri,
            "genres": self.genres or [],
            "image_url": self.image_url,
        }
