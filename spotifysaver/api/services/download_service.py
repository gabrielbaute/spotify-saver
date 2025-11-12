"""Download service for API operations"""

import asyncio
from pathlib import Path
from typing import Dict, Optional, Callable, Any

from ...services import SpotifyAPI, YoutubeMusicSearcher
from ...downloader import YouTubeDownloader, YouTubeDownloaderForCLI
from ...enums import AudioFormat, Bitrate
from ...spotlog import get_logger
from ..config import APIConfig

logger = get_logger("DownloadService")


class DownloadService:
    """Service class for handling download operations via API."""

    def __init__(
        self,
        output_dir: Optional[str] = None,
        download_lyrics: bool = False,
        download_cover: bool = True,
        generate_nfo: bool = False,
        output_format: str = "m4a",
        bit_rate: int = 128,
    ):
        """Initialize the download service.

        Args:
            output_dir: Custom output directory
            download_lyrics: Whether to download lyrics
            download_cover: Whether to download cover art
            generate_nfo: Whether to generate NFO files
            output_format: Audio format for downloads
        """
        self.output_dir = output_dir or APIConfig.get_output_dir()
        self.download_lyrics = download_lyrics
        self.download_cover = download_cover
        self.generate_nfo = generate_nfo
        # Convert string format to enum for internal use
        self.output_format = YouTubeDownloader.string_to_audio_format(output_format)
        self.bit_rate = YouTubeDownloader.int_to_bitrate(bit_rate)

        # Initialize services
        self.spotify = SpotifyAPI()
        self.searcher = YoutubeMusicSearcher()
        self.downloader = YouTubeDownloaderForCLI(base_dir=self.output_dir)

    async def download_from_url(
        self,
        spotify_url: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> Dict[str, Any]:
        """Download content from a Spotify URL.

        Args:
            spotify_url: Spotify URL to download
            progress_callback: Optional callback for progress updates

        Returns:
            Dict containing download results and statistics
        """
        try:
            if "track" in spotify_url:
                return await self._download_track(spotify_url, progress_callback)
            elif "album" in spotify_url:
                return await self._download_album(spotify_url, progress_callback)
            elif "playlist" in spotify_url:
                return await self._download_playlist(spotify_url, progress_callback)
            else:
                raise ValueError("Invalid Spotify URL type")

        except Exception as e:
            logger.error(f"Error downloading from {spotify_url}: {str(e)}")
            raise

    async def _download_track(
        self,
        track_url: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> Dict[str, Any]:
        """Download a single track."""
        track = self.spotify.get_track(track_url)

        if progress_callback:
            progress_callback(1, 1, track.name)

        # Run download in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        audio_path, updated_track = await loop.run_in_executor(
            None, self._download_track_sync, track
        )

        return {
            "content_type": "track",
            "completed_tracks": 1 if audio_path else 0,
            "failed_tracks": 0 if audio_path else 1,
            "total_tracks": 1,
            "output_directory": str(audio_path.parent) if audio_path else None,
        }

    async def _download_album(
        self,
        album_url: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> Dict[str, Any]:
        """Download an entire album."""
        album = self.spotify.get_album(album_url)

        # Create a wrapper for the progress callback
        def sync_progress_callback(idx: int, total: int, name: str):
            if progress_callback:
                progress_callback(idx, total, name)

        # Run download in thread pool
        loop = asyncio.get_event_loop()
        success, total = await loop.run_in_executor(
            None,
            self.downloader.download_album_cli,
            album,
            self.download_lyrics,
            self.output_format,
            self.bit_rate,
            self.generate_nfo,
            self.download_cover,
            sync_progress_callback,
        )

        output_dir = self.downloader._get_album_dir(album)

        return {
            "content_type": "album",
            "completed_tracks": success,
            "failed_tracks": total - success,
            "total_tracks": total,
            "output_directory": str(output_dir),
        }

    async def _download_playlist(
        self,
        playlist_url: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> Dict[str, Any]:
        """Download an entire playlist."""
        playlist = self.spotify.get_playlist(playlist_url)

        # Create a wrapper for the progress callback
        def sync_progress_callback(idx: int, total: int, name: str):
            if progress_callback:
                progress_callback(idx, total, name)

        # Run download in thread pool
        loop = asyncio.get_event_loop()
        success, total = await loop.run_in_executor(
            None,
            self.downloader.download_playlist_cli,
            playlist,
            self.output_format,
            self.bit_rate,
            self.download_lyrics,
            self.download_cover,
            sync_progress_callback,
        )

        output_dir = Path(self.output_dir) / playlist.name

        return {
            "content_type": "playlist",
            "completed_tracks": success,
            "failed_tracks": total - success,
            "total_tracks": total,
            "output_directory": str(output_dir),
        }

    def _download_track_sync(self, track):
        """Synchronous track download helper."""
        return self.downloader.download_track_cli(
            track, 
            output_format=self.output_format, 
            bitrate=self.bit_rate,
            download_lyrics=self.download_lyrics
        )
