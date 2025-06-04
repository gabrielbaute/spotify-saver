from dataclasses import dataclass
from typing import List


@dataclass
class Artist:
    """Representa un artista individual con su metadata."""

    name: str
    uri: str
    genres: List[str] = None
    popularity: int = None
    followers: int = None
    image_url: str = None

    def to_dict(self) -> dict:
        """Convierte el objeto a un diccionario para serialización."""
        return {
            "name": self.name,
            "uri": self.uri,
            "genres": self.genres or [],
            "popularity": self.popularity,
            "followers": self.followers,
            "image_url": self.image_url,
        }
