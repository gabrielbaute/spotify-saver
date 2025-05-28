from dataclasses import dataclass
from typing import List

@dataclass
class Track:
    """Representa un track individual con su metadata."""
    number: int
    total_tracks: int
    name: str
    duration: int
    uri: str
    artists: List[str]
    release_date: str
    genres: List[str] = None
    album_name: str = None
    cover_url: str = None

    def to_dict(self) -> dict:
        """Convierte el objeto a un diccionario para serialización."""
        return {
            "number": self.number,
            "total_tracks": self.total_tracks,
            "name": self.name,
            "duration": self.duration,
            "uri": self.uri,
            "artists": self.artists,
            "album": self.album_name,
            "release_date": self.release_date,
            "genres": self.genres if self.genres else [],
            "cover_url": self.cover_url
        }
