from pydantic import BaseModel
from typing import List, Optional

class AlbumDescription(BaseModel):
    """
    Response Schema for Album metadata from TheAudioDB.

    keywords:
        language (str): Language of the description
        description (str): Description of the album
    """
    language: str
    description: str

class MediaAlbumURLs(BaseModel):
    """
    Response Schema for Album URLs from TheAudioDB.

    keywords:
        thumb_url (Optional[str]): URL of the album thumbnail
        back_url (Optional[str]): URL of the album back cover
        cd_art_url (Optional[str]): URL of the album CD art
        case_url (Optional[str]): URL of the album 3D case
        face_url (Optional[str]): URL of the album face
        flat_url (Optional[str]): URL of the album 3D flat
        cd_thumb_url (Optional[str]): URL of the album 3D thumbnail
    """
    thumb_url: Optional[str]
    back_url: Optional[str]
    cd_art_url: Optional[str]
    case_url: Optional[str]
    face_url: Optional[str]
    flat_url: Optional[str]
    cd_thumb_url: Optional[str]

class AlbumADBResponse(BaseModel):
    """
    Response Schema for Album metadata from TheAudioDB.

    keywords:
        id (int): ID of the album in TheAudioDB
        name (str): Name of the album
        artist_id (int): ID of the artist in TheAudioDB
        artist_name (str): Name of the artist
        genre (Optional[str]): Genre of the album
        style (Optional[str]): Style of the album
        mood (Optional[str]): Mood of the album
        musicbrainz_id (Optional[str]): MusicBrainz ID of the album
        artist_musicbrainz_id (Optional[str]): MusicBrainz ID of the artist
        release_format (Optional[str]): Release format of the album
        release_date (Optional[str]): Release date of the album
        description (Optional[List[AlbumDescription]]): List of descriptions of the album
        media_album (Optional[MediaAlbumURLs]): URLs of the album media
    """
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