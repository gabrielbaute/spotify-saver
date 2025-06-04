from dataclasses import dataclass
from typing import List
from .track import Track


@dataclass
class Album:
    """Representa un álbum y sus tracks."""

    name: str
    artists: List[str]
    release_date: str
    genres: List[str]
    cover_url: str
    tracks: List[Track]

    def get_track_by_uri(self, uri: str) -> Track | None:
        """Busca un track por su URI de Spotify."""
        return next((t for t in self.tracks if t.uri == uri), None)
