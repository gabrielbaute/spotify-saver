"""Track model for SpotifySaver."""

from dataclasses import dataclass, replace
from typing import List, Optional


@dataclass(frozen=True)
class Track:
    """Represents an individual track with its metadata.
    
    This class encapsulates all the information about a music track including
    basic metadata, source information, and optional features like lyrics.
    
    Attributes:
        number: Track number in the album/playlist
        total_tracks: Total number of tracks in the source collection
        name: The name/title of the track
        duration: Duration of the track in seconds
        uri: Spotify URI for the track
        artists: List of artist names
        release_date: Release date of the track/album
        disc_number: Disc number (for multi-disc albums)
        source_type: Type of source ("album" or "playlist")
        playlist_name: Name of the playlist if source is playlist
        genres: List of genres associated with the track
        album_name: Name of the album containing this track
        cover_url: URL to the cover art image
        has_lyrics: Whether lyrics have been successfully downloaded
    """

    number: int
    total_tracks: int
    name: str
    duration: int
    uri: str
    artists: List[str]
    album_artist: List[str]
    release_date: str
    disc_number: int = 1
    source_type: str = "album"
    playlist_name: Optional[str] = None
    genres: List[str] = None
    album_name: str = None
    cover_url: str = None
    has_lyrics: bool = False

    def __hash__(self):
        """Generate hash based on track name, artists, and duration.
        
        Returns:
            int: Hash value for the track instance
        """
        return hash((self.name, tuple(self.artists), self.duration))

    def with_lyrics_status(self, success: bool) -> "Track":
        """Return a new Track instance with updated lyrics status.
        
        Args:
            success: Whether lyrics were successfully downloaded
            
        Returns:
            Track: New Track instance with updated has_lyrics field
        """
        return replace(self, has_lyrics=success)

    @property
    def lyrics_filename(self) -> str:
        """Generate a safe filename for LRC lyrics files.
        
        Returns:
            str: Safe filename with .lrc extension
        """
        return f"{self.name.replace('/', '-')}.lrc"

    def to_dict(self) -> dict:
        """Convert track to dictionary format.
        
        Returns:
            dict: Dictionary representation of the track with lyrics_available field
        """
        return {
            **{k: v for k, v in self.__dict__.items() if k != "has_lyrics"},
            "lyrics_available": self.has_lyrics,
        }
