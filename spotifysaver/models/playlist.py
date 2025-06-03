# playlist.py
from dataclasses import dataclass
from typing import List
from .track import Track

@dataclass
class Playlist:
    """Representa una playlist de Spotify y sus tracks."""
    name: str
    description: str
    owner: str
    uri: str
    cover_url: str
    tracks: List[Track]

    def get_track_by_uri(self, uri: str) -> Track | None:
        """Busca un track por su URI (similar al método de Album)."""
        return next((t for t in self.tracks if t.uri == uri), None)