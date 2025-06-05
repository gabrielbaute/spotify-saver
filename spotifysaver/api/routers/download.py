"""Download endpoints for the SpotifySaver API"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from ..schemas import (
    DownloadRequest,
    DownloadResponse,
    DownloadStatus,
    ErrorResponse,
    AlbumInfo,
    PlaylistInfo,
    TrackInfo,
)
from ..services import DownloadService
from ...services import SpotifyAPI
from ...spotlog import get_logger

logger = get_logger("API")
router = APIRouter()

# In-memory task storage (in production, use Redis or database)
tasks: Dict[str, DownloadStatus] = {}


@router.post("/download", response_model=DownloadResponse)
async def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Start a download task for a Spotify URL.

    This endpoint initiates the download process and returns a task ID
    that can be used to track the progress of the download.
    """
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())

        # Determine content type from URL
        spotify_url = str(request.spotify_url)
        if "track" in spotify_url:
            content_type = "track"
        elif "album" in spotify_url:
            content_type = "album"
        elif "playlist" in spotify_url:
            content_type = "playlist"
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid Spotify URL. Must be a track, album, or playlist.",
            )

        # Create initial task status
        task_status = DownloadStatus(
            task_id=task_id,
            status="pending",
            progress=0,
            total_tracks=0,
            completed_tracks=0,
            failed_tracks=0,
            started_at=datetime.now().isoformat(),
        )
        tasks[task_id] = task_status

        # Start background download task
        background_tasks.add_task(download_task, task_id, request)

        logger.info(f"Started download task {task_id} for {spotify_url}")

        return DownloadResponse(
            task_id=task_id,
            status="pending",
            spotify_url=spotify_url,
            content_type=content_type,
            message=f"Download task started for {content_type}",
        )

    except Exception as e:
        logger.error(f"Error starting download: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{task_id}/status", response_model=DownloadStatus)
async def get_download_status(task_id: str):
    """Get the current status of a download task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    return tasks[task_id]


@router.get("/download/{task_id}/cancel")
async def cancel_download(task_id: str):
    """Cancel a download task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]
    if task.status in ["completed", "failed"]:
        raise HTTPException(
            status_code=400, detail=f"Cannot cancel task with status: {task.status}"
        )

    task.status = "cancelled"
    task.error_message = "Task cancelled by user"

    return {"message": "Task cancelled successfully"}


@router.get("/downloads")
async def list_downloads():
    """List all download tasks."""
    return {"tasks": list(tasks.values())}


@router.get("/inspect")
async def inspect_spotify_url(spotify_url: str):
    """Inspect a Spotify URL to get metadata without downloading."""
    try:
        spotify = SpotifyAPI()
        if "track" in spotify_url:
            track = spotify.get_track(spotify_url)
            return TrackInfo(
                name=track.name,
                artists=track.artists,
                album_name=track.album_name,
                duration=track.duration,
                number=track.number if hasattr(track, "number") else 1,
                uri=track.uri,
            )

        elif "album" in spotify_url:
            album = spotify.get_album(spotify_url)
            tracks = [
                TrackInfo(
                    name=t.name,
                    artists=t.artists,
                    album_name=t.album_name,
                    duration=t.duration,
                    number=t.number,
                    uri=t.uri,
                )
                for t in album.tracks
            ]
            return AlbumInfo(
                name=album.name,
                artists=album.artists,
                release_date=album.release_date,
                total_tracks=len(album.tracks),
                cover_url=album.cover_url,
                tracks=tracks,
            )

        elif "playlist" in spotify_url:
            playlist = spotify.get_playlist(spotify_url)
            tracks = [
                TrackInfo(
                    name=t.name,
                    artists=t.artists,
                    album_name=t.album_name,
                    duration=t.duration,
                    number=t.number,
                    uri=t.uri,
                )
                for t in playlist.tracks
            ]
            return PlaylistInfo(
                name=playlist.name,
                owner=playlist.owner,
                description=playlist.description,
                total_tracks=len(playlist.tracks),
                cover_url=playlist.cover_url,
                tracks=tracks,
            )

        else:
            raise HTTPException(status_code=400, detail="Invalid Spotify URL")

    except Exception as e:
        logger.error(f"Error inspecting URL {spotify_url}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def download_task(task_id: str, request: DownloadRequest):
    """Background task for handling downloads."""
    try:
        task = tasks[task_id]
        task.status = "processing"

        # Initialize the download service
        download_service = DownloadService(
            output_dir=request.output_dir,
            download_lyrics=request.download_lyrics,
            download_cover=request.download_cover,
            generate_nfo=request.generate_nfo,
            output_format=request.output_format,
        )

        # Progress callback
        def progress_callback(current: int, total: int, track_name: str):
            task.current_track = track_name
            task.completed_tracks = current - 1  # current is 1-based
            task.total_tracks = total
            task.progress = int((current / total) * 100) if total > 0 else 0

        # Perform the download
        result = await download_service.download_from_url(
            str(request.spotify_url), progress_callback=progress_callback
        )

        # Update task status
        task.status = "completed"
        task.progress = 100
        task.completed_tracks = result.get("completed_tracks", 0)
        task.failed_tracks = result.get("failed_tracks", 0)
        task.output_directory = result.get("output_directory")
        task.completed_at = datetime.now().isoformat()

        logger.info(f"Download task {task_id} completed successfully")

    except Exception as e:
        logger.error(f"Download task {task_id} failed: {str(e)}")
        task = tasks[task_id]
        task.status = "failed"
        task.error_message = str(e)
        task.completed_at = datetime.now().isoformat()
