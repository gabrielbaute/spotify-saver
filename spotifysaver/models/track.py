"""Track model for SpotifySaver."""

from dataclasses import dataclass, replace
from typing import List, Optional


@dataclass(frozen=True)
class Track:
    """Representa un track individual con su metadata."""

    number: int
    total_tracks: int
    name: str
    duration: int
    uri: str
    artists: List[str]
    release_date: str
    disc_number: int = 1
    source_type: str = "album"
    playlist_name: Optional[str] = None
    genres: List[str] = None
    album_name: str = None
    cover_url: str = None
    has_lyrics: bool = False

    def __hash__(self):
        return hash((self.name, tuple(self.artists), self.duration))

    def with_lyrics_status(self, success: bool) -> "Track":
        """Devuelve una NUEVA instancia con el estado actualizado"""
        return replace(self, has_lyrics=success)

    @property
    def lyrics_filename(self) -> str:
        """Nombre seguro para archivos LRC."""
        return f"{self.name.replace('/', '-')}.lrc"

    def to_dict(self) -> dict:
        """Versión compatible con el estado has_lyrics."""
        return {
            **{k: v for k, v in self.__dict__.items() if k != "has_lyrics"},
            "lyrics_available": self.has_lyrics,
        }
