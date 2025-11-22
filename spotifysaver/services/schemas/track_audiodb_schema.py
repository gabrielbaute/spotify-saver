from pydantic import BaseModel
from typing import List, Optional

class TrackADBResponse(BaseModel):
    """
    Response Schema for Track metadata from TheAudioDB.

    keywords:
        id (int): ID of the track in TheAudioDB
        name (str): Name of the track
        album_id (int): ID of the album containing the track in TheAudioDB
        album_name (str): Name of the album containing the track
        artist_id (List[int]): List of IDs of the artists in TheAudioDB
        artist_name (List[str]): List of names of the artists
        duration (int): Duration of the track in seconds
        track_number (int): Track number in the album
        genre (Optional[str]): Genre of the track
        mood (Optional[str]): Mood of the track
        style (Optional[str]): Style of the track
        lyrics (Optional[str]): Lyrics of the track
        musicbrainz_id (Optional[str]): MusicBrainz ID of the track
        album_musicbrainz_id (Optional[str]): MusicBrainz ID of the album
        artist_musicbrainz_id (Optional[str]): MusicBrainz ID of the artist
    """
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