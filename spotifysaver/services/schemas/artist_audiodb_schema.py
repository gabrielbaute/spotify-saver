from pydantic import BaseModel
from typing import List, Optional

class ArtistBiography(BaseModel):
    language: str
    biography: str

class ArtistFanart(BaseModel):
    number: int
    url: str

class MediaArtistURLs(BaseModel):
    thumb_url: Optional[str]
    logo_url: Optional[str]
    clearart_url: Optional[str]
    wide_thumb_url: Optional[str]
    banner_url: Optional[str]
    fanarts: Optional[List[ArtistFanart]]

class ArtistADBResponse(BaseModel):
    id: int
    name: str
    gender: Optional[str]
    country: Optional[str]
    born_year: Optional[int]
    die_year: Optional[int]
    style: Optional[str]
    genre: Optional[str]
    mood: Optional[str]
    musicbrainz_id: Optional[str]
    briographies: Optional[List[ArtistBiography]]