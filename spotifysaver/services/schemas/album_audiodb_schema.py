from pydantic import BaseModel
from typing import Dict, List, Optional

class AlbumDescription(BaseModel):
    language: str
    description: str

class MediaAlbumURLs(BaseModel):
    thumb_url: Optional[str]
    back_url: Optional[str]
    cd_art_url: Optional[str]
    case_url: Optional[str]
    face_url: Optional[str]
    flat_url: Optional[str]
    cd_thumb_url: Optional[str]

class AlbumADBResponse(BaseModel):
    id: int
    name: str
    artist_id: int
    artist_name: str
    genre: Optional[str]
    style: Optional[str]
    mood: Optional[str]
    musicbrainz_id: Optional[str]
    artist_musicbrainz_id: Optional[str]
    release_format: Optional[str]
    release_date: Optional[str]
    description: Optional[List[AlbumDescription]]
    media_album: Optional[MediaAlbumURLs]