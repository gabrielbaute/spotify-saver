from pydantic import BaseModel
from typing import List, Optional

class ArtistBiography(BaseModel):
    """
    Response Schema for Artist metadata from TheAudioDB.

    keywords:
        language (str): Language of the biography
        biography (str): Biography of the artist
    """
    language: str
    biography: str

class MediaArtistURLs(BaseModel):
    """
    Response Schema for Artist URLs from TheAudioDB.

    keywords:
        thumb_url (Optional[str]): URL of the artist thumbnail
        logo_url (Optional[str]): URL of the artist logo
        clearart_url (Optional[str]): URL of the artist clear art
        wide_thumb_url (Optional[str]): URL of the artist wide thumbnail
        banner_url (Optional[str]): URL of the artist banner
        fanarts (Optional[str]): URL of the artist fanart
    """
    thumb_url: Optional[str]
    logo_url: Optional[str]
    clearart_url: Optional[str]
    wide_thumb_url: Optional[str]
    banner_url: Optional[str]
    fanarts: Optional[str]

class ArtistADBResponse(BaseModel):
    """
    Response Schema for Artist metadata from TheAudioDB.

    keywords:
        id (int): ID of the artist in TheAudioDB
        name (str): Name of the artist
        gender (Optional[str]): Gender of the artist
        country (Optional[str]): Country of the artist
        born_year (Optional[int]): Year of birth of the artist
        die_year (Optional[int]): Year of death of the artist
        style (Optional[str]): Style of the artist
        genre (Optional[str]): Genre of the artist
        mood (Optional[str]): Mood of the artist
        musicbrainz_id (Optional[str]): MusicBrainz ID of the artist
        media_artist (Optional[MediaArtistURLs]): URLs of the artist media
        biography (Optional[ArtistBiography]): Biography of the artist
    """
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
    media_artist: Optional[MediaArtistURLs]
    briographies: Optional[List[ArtistBiography]]