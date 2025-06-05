"""Pydantic schemas for API requests and responses"""

from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field


class DownloadRequest(BaseModel):
    """Schema for download request."""
    
    spotify_url: HttpUrl = Field(
        ..., 
        description="Spotify URL for track, album, or playlist",
        example="https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy"
    )
    download_lyrics: bool = Field(
        default=False, 
        description="Whether to download synchronized lyrics"
    )
    download_cover: bool = Field(
        default=True, 
        description="Whether to download cover art"
    )
    generate_nfo: bool = Field(
        default=False, 
        description="Whether to generate NFO metadata files"
    )
    output_format: str = Field(
        default="m4a", 
        description="Audio format for downloaded files",
        pattern="^(m4a|mp3)$"
    )
    output_dir: Optional[str] = Field(
        default=None,
        description="Custom output directory (optional)"
    )


class TrackInfo(BaseModel):
    """Schema for track information."""
    
    name: str
    artists: List[str]
    album_name: Optional[str] = None
    duration: int  # in seconds
    number: int
    uri: str


class AlbumInfo(BaseModel):
    """Schema for album information."""
    
    name: str
    artists: List[str]
    release_date: str
    total_tracks: int
    cover_url: Optional[str] = None
    tracks: List[TrackInfo]


class PlaylistInfo(BaseModel):
    """Schema for playlist information."""
    
    name: str
    owner: str
    description: Optional[str] = None
    total_tracks: int
    cover_url: Optional[str] = None
    tracks: List[TrackInfo]


class DownloadResponse(BaseModel):
    """Schema for download response."""
    
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Current status of the download")
    spotify_url: str = Field(..., description="Original Spotify URL")
    content_type: str = Field(..., description="Type of content (track, album, playlist)")
    message: str = Field(..., description="Status message")


class DownloadStatus(BaseModel):
    """Schema for download status."""
    
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    current_track: Optional[str] = None
    total_tracks: int = 0
    completed_tracks: int = 0
    failed_tracks: int = 0
    output_directory: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
