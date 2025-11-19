from pydantic import BaseModel
from typing import List, Optional

class TrackADBResponse(BaseModel):
    id: int
    name: str
    album_id: int
    album_name: str
    artist_id: List[int]
    artist_name: List[str]
    duration: int
    track_number: int
    genre: Optional[str]
    mood: Optional[str]
    style: Optional[str]
    lyrics: Optional[str]
    musicbrainz_id: Optional[str]
    album_musicbrainz_id: Optional[str]
    artist_musicbrainz_id: Optional[str]