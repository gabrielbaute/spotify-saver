from dataclasses import dataclass
from typing import List

@dataclass
class Track:
    """Representa un track individual con su metadata."""
    number: int
    name: str
    duration: int
    uri: str
    artists: List[str]
    release_date: str
    album_name: str = None
    cover_url: str = None

    def to_dict(self) -> dict:
        """Convierte el objeto a un diccionario para serialización."""
        return {
            "number": self.number,
            "name": self.name,
            "duration": self.duration,
            "artists": self.artists,
            "album": self.album_name,
            "release_date": self.release_date,
            "cover_url": self.cover_url
        }
