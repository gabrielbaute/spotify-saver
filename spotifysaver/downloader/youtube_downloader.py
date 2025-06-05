"""Youtube Downloader Module"""

import logging
from pathlib import Path
from typing import Optional

import requests
import yt_dlp
from mutagen.mp4 import MP4, MP4Cover

from spotifysaver.services import YoutubeMusicSearcher, LrclibAPI
from spotifysaver.metadata import NFOGenerator
from spotifysaver.models import Track, Album, Playlist
from spotifysaver.config import Config
from spotifysaver.spotlog import get_logger

logger = get_logger("YoutubeDownloader")


class YouTubeDownloader:
    """Downloads tracks from YouTube Music and adds Spotify metadata.
    
    This class handles the complete download process including audio download,
    metadata injection, lyrics fetching, and file organization.
    
    Attributes:
        base_dir: Base directory for music downloads
        searcher: YouTube Music searcher instance
        lrc_client: LRC Lib API client for lyrics
    """

    def __init__(self, base_dir: str = "Music"):
        """Initialize the YouTube downloader.
        
        Args:
            base_dir: Base directory where music will be downloaded
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.searcher = YoutubeMusicSearcher()
        self.lrc_client = LrclibAPI()

    def _get_ydl_opts(self, output_path: Path) -> dict:
        """Get robust yt-dlp configuration with cookie support.
        
        Args:
            output_path: Path where the file should be saved
            
        Returns:
            dict: yt-dlp configuration options
        """
        is_verbose = logger.getEffectiveLevel() <= logging.DEBUG
        ytm_base_url = "https://music.youtube.com"

        opts = {
            "format": "m4a/bestaudio[abr<=128]/best",
            "outtmpl": str(output_path.with_suffix(".%(ext)s")),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                }
            ],
            "quiet": not is_verbose,
            "verbose": is_verbose,
            "extract_flat": False,
            "logger": self._get_ydl_logger(),
            # Parámetros de cookies y headers para evitar bloqueos
            "cookiefile": (
                str(Config.YTDLP_COOKIES_PATH) if Config.YTDLP_COOKIES_PATH else None
            ),
            "referer": ytm_base_url,
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            ),
            "extractor_args": {
                "youtube": {
                    "player_client": ["web", "android_music"],
                    "player_skip": ["configs"],
                }
            },
            "retries": 5,
            "fragment_retries": 5,
            "skip_unavailable_fragments": True,
        }

        return opts

    def _get_ydl_logger(self):
        """Create a yt-dlp logger that integrates with the application logger.
        
        Returns:
            YDLLogger: Custom logger for yt-dlp integration
        """

        class YDLLogger:
            def debug(self, msg):
                logger.debug(f"[yt-dlp] {msg}")

            def info(self, msg):
                logger.info(f"[yt-dlp] {msg}")

            def warning(self, msg):
                logger.warning(f"[yt-dlp] {msg}")

            def error(self, msg):
                logger.error(f"[yt-dlp] {msg}")

        return YDLLogger()

    def _get_output_path(self, track: Track, album_artist: str = None) -> Path:
        """Generate output paths: Music/Artist/Album (Year)/Track.m4a.
        
        Args:
            track: Track object containing metadata
            album_artist: Artist name for album organization
            
        Returns:
            Path: Complete file path where the track should be saved
        """
        if track.source_type == "playlist":
            dir_path = self.base_dir / track.playlist_name
        else:
            artist_name = album_artist or track.artists[0] if track.artists else "Unknown Artist"
            dir_path = (
                self.base_dir
                / album_artist
                / f"{track.album_name} ({track.release_date[:4]})"
            )

        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path / f"{track.name}.m4a"

    def _download_cover(self, track: Track) -> Optional[bytes]:
        """Download cover art from Spotify.
        
        Args:
            track: Track object containing cover URL
            
        Returns:
            bytes: Cover art image data, or None if download failed
        """
        if not track.cover_url:
            return None
        try:
            response = requests.get(track.cover_url, timeout=10)
            return response.content if response.status_code == 200 else None
        except Exception as e:
            logger.error(f"Error downloading cover: {e}")
            return None

    def _add_metadata(self, file_path: Path, track: Track, cover_data: Optional[bytes]):
        """Add metadata and cover art using Mutagen MP4 tags.
        
        Args:
            file_path: Path to the audio file
            track: Track object with metadata
            cover_data: Cover art image data
            
        Raises:
            Exception: If metadata addition fails
        """
        try:
            audio = MP4(file_path)

            # Basic metadata (using standard MP4 tags)
            audio["\xa9nam"] = [track.name]  # Título (¡Debe ser una lista!)
            audio["\xa9ART"] = [";".join(track.artists)]  # Artista
            audio["\xa9alb"] = [track.album_name]  # Álbum
            audio["\xa9day"] = [track.release_date[:4]]  # Year only
            audio["trkn"] = [
                (track.number, track.total_tracks)
            ]  # Número de pista y total
            audio["disk"] = [
                (track.disc_number, 1)
            ]  # Disc number (assuming 1 disc)

            # Genre (if exists in track)
            if hasattr(track, "genres") and track.genres:
                audio["\xa9gen"] = [";".join(track.genres)]

            # Cover art
            if cover_data:
                audio["covr"] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]

            audio.save()
            logger.info(f"Metadata added to {file_path}")

        except Exception as e:
            logger.error(f"Error adding metadata: {str(e)}")
            raise

    def _save_lyrics(self, track: "Track", audio_path: Path) -> bool:
        """Save synchronized lyrics as .lrc file.
        
        Args:
            track: Track object for lyrics search
            audio_path: Path to the audio file (used to determine .lrc path)
            
        Returns:
            bool: True if lyrics were successfully saved, False otherwise
        """
        try:
            lyrics = self.lrc_client.get_lyrics_with_fallback(track)
            if not lyrics or "[instrumental]" in lyrics.lower():
                return False

            lrc_path = audio_path.with_suffix(".lrc")
            lrc_path.write_text(lyrics, encoding="utf-8")

            if lrc_path.stat().st_size > 0:
                logger.info(f"Lyrics saved in: {lrc_path}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error saving song lyrics: {str(e)}", exc_info=True)
            return False

    def _get_album_dir(self, album: "Album") -> Path:
        """Get the album directory path.
        
        Args:
            album: Album object containing metadata
            
        Returns:
            Path: Directory path for the album
        """
        artist_dir = self.base_dir / album.artists[0]
        return artist_dir / f"{album.name} ({album.release_date[:4]})"

    def _save_cover_album(self, url: str, output_path: Path):
        """Download and save album cover art.
        
        Args:
            url: URL of the cover image
            output_path: Path where the cover should be saved
        """
        if not url:
            return

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                output_path.write_bytes(response.content)
        except Exception as e:
            logger.error(f"Error downloading cover: {e}")

    def download_track(
        self,
        track: Track,
        yt_url: str,
        album_artist: str = None,
        download_lyrics: bool = False,
    ) -> tuple[Optional[Path], Optional[Track]]:
        """Download a track from YouTube Music with Spotify metadata.

        Args:
            track: Track object with metadata
            yt_url: YouTube Music URL for the track
            album_artist: Artist name for file organization
            download_lyrics: Whether to download lyrics

        Returns:
            tuple: (Downloaded file path, Updated track) or (None, None) on error
        """
        output_path = self._get_output_path(track, album_artist)
        yt_url = self.searcher.search_track(track)
        ydl_opts = self._get_ydl_opts(output_path)

        if not yt_url:
            logger.error(f"No match found for: {track.name}")
            return None, None

        try:
            # 1. Descarga el audio
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([yt_url])

            # 2. Add metadata and cover art
            cover_data = self._download_cover(track)
            self._add_metadata(output_path, track, cover_data)

            # 3. Lyrics handling
            updated_track = track
            if download_lyrics:
                success = self._save_lyrics(track, output_path)
                updated_track = track.with_lyrics_status(success)

            logger.info(f"Download completed: {output_path}")
            return output_path, updated_track

        except Exception as e:
            logger.error(f"Error downloading {track.name}: {e}", exc_info=True)
            if output_path.exists():
                logger.debug(f"Removing corrupt file: {output_path}")
                output_path.unlink()
            return None, None

    def download_album(
        self,
        album: Album,
        download_lyrics: bool = False,
        nfo: bool = False,
        cover: bool = False,
    ):
        """Download a complete album and generate metadata.
        
        Args:
            album: Album object to download
            download_lyrics: Whether to download lyrics for tracks
            nfo: Whether to generate NFO metadata file
            cover: Whether to download album cover
        """
        for track in album.tracks:
            yt_url = self.searcher.search_track(track)
            self.download_track(
                track,
                yt_url,
                album_artist=album.artists[0],
                download_lyrics=download_lyrics,
            )

        output_dir = self._get_album_dir(album)

        # Generar NFO después de descargar todos los tracks
        if nfo:
            logger.info(f"Generating NFO for album: {album.name}")
            NFOGenerator.generate(album, output_dir)

        # Download cover art
        if cover and album.cover_url:
            logger.info(f"Downloading cover for album: {album.name}")
            self._save_cover_album(album.cover_url, output_dir / "cover.jpg")

        pass

    def download_album_cli(
        self,
        album: Album,        download_lyrics: bool = False,
        nfo: bool = False,  # Generate NFO
        cover: bool = False,  # Download cover art
        progress_callback: Optional[callable] = None,  # Progress callback
    ) -> tuple[int, int]:  # Returns (success, total)
        """Download a complete album with progress support.

        Args:
            album: Album object to download
            download_lyrics: Whether to download lyrics
            nfo: Whether to generate NFO file
            cover: Whether to download cover art
            progress_callback: Function that receives (current_track, total_tracks, track_name).
                            Example: lambda idx, total, name: print(f"{idx}/{total} {name}")

        Returns:
            tuple: (successful_downloads, total_tracks)
        """
        if not album.tracks:
            logger.error("Álbum no contiene tracks.")
            return 0, 0

        success = 0
        for idx, track in enumerate(album.tracks, 1):
            try:
                if progress_callback:
                    progress_callback(idx, len(album.tracks), track.name)

                yt_url = self.searcher.search_track(track)
                if not yt_url:
                    raise ValueError(f"No se encontró en YouTube Music: {track.name}")

                audio_path, _ = self.download_track(
                    track,
                    yt_url,
                    album_artist=album.artists[0],
                    download_lyrics=download_lyrics,
                )
                if audio_path:
                    success += 1
            except Exception as e:
                logger.error(f"Error en track {track.name}: {str(e)}")

        # Generar metadatos solo si hay éxitos
        if success > 0:
            output_dir = self._get_album_dir(album)
            if nfo:
                NFOGenerator.generate(album, output_dir)
            if cover and album.cover_url:
                self._save_cover_album(album.cover_url, output_dir / "cover.jpg")

        return success, len(album.tracks)

    def download_playlist(
        self,
        playlist: Playlist,
        download_lyrics: bool = False,
        cover: bool = False,
        nfo: bool = False,
    ):
        """Download a complete playlist and generate metadata.
        
        Args:
            playlist: Playlist object to download
            download_lyrics: Whether to download lyrics
            cover: Whether to download playlist cover
            nfo: Whether to generate NFO file
            
        Returns:
            bool: True if at least one track was successfully downloaded
        """

        # Validación básica
        if not playlist.name:
            logger.error("Playlist name is empty. Cannot create directory.")
            return False
        if not playlist.tracks:
            logger.warning(f"Playlist '{playlist.name}' has no tracks.")
            return False

        # Configuración inicial
        output_dir = self.base_dir / playlist.name
        output_dir.mkdir(parents=True, exist_ok=True)
        success = False
        failed_tracks = []

        # Descarga de tracks
        for track in playlist.tracks:
            try:
                # Descargar URL de YouTube
                _, updated_track = self.download_track(
                    track, download_lyrics=download_lyrics
                )
                if updated_track:
                    success = True
            except Exception as e:
                failed_tracks.append(track.name)
                logger.error(f"Error downloading track {track.name}: {e}")        # Download cover art (only if successful)
        if success and playlist.cover_url and cover:
            logger.info(f"Downloading cover for playlist: {playlist.name}")
            self._save_cover_album(playlist.cover_url, output_dir / "cover.jpg")

        # Generate NFO (only if successful)
        if success and nfo:
            logger.info(f"Generating NFO for playlist: {playlist.name}")
            NFOGenerator.generate(playlist, output_dir)

        # Log results
        if failed_tracks:
            logger.warning(
                f"Failed downloads in playlist '{playlist.name}': {len(failed_tracks)}/{len(playlist.tracks)}. "
                f"Ejemplos: {', '.join(failed_tracks[:3])}{'...' if len(failed_tracks) > 3 else ''}"
            )

        return success

    def download_playlist_cli(
        self,
        playlist: Playlist,
        download_lyrics: bool = False,
        cover: bool = False,
        progress_callback: Optional[callable] = None,
    ) -> tuple[int, int]:
        """Download a complete playlist with progress bar support.

        Args:
            playlist: Playlist object to download
            download_lyrics: Whether to download lyrics
            cover: Whether to download playlist cover
            progress_callback: Function that receives (current_track, total_tracks, track_name).
                            Example: lambda idx, total, name: print(f"{idx}/{total} {name}")

        Returns:
            tuple: (successful_downloads, total_tracks)
        """
        if not playlist.name or not playlist.tracks:
            logger.error("Playlist inválida: sin nombre o tracks vacíos")
            return 0, 0

        output_dir = self.base_dir / playlist.name
        output_dir.mkdir(parents=True, exist_ok=True)
        success = 0

        for idx, track in enumerate(playlist.tracks, 1):
            try:
                # Notificar progreso (si hay callback)
                if progress_callback:
                    progress_callback(idx, len(playlist.tracks), track.name)

                yt_url = self.searcher.search_track(track)
                _, updated_track = self.download_track(
                    track, yt_url, download_lyrics=download_lyrics
                )
                if updated_track:
                    success += 1
            except Exception as e:
                logger.error(f"Error en {track.name}: {str(e)}")

        if success > 0 and cover and playlist.cover_url:
            try:
                self._save_cover_album(playlist.cover_url, output_dir / "cover.jpg")
            except Exception as e:
                logger.error(f"Error downloading playlist cover: {str(e)}")

        return success, len(playlist.tracks)
