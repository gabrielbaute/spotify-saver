"""Youtube Downloader Module"""

import logging
import re
import requests
import yt_dlp
from pathlib import Path
from typing import Optional

from spotifysaver.services import YoutubeMusicSearcher, LrclibAPI
from spotifysaver.metadata import NFOGenerator, MusicFileMetadata
from spotifysaver.downloader.image_downloader import ImageDownloader
from spotifysaver.models import Track, Album, Playlist
from spotifysaver.enums import AudioFormat, Bitrate
from spotifysaver.config import Config
from spotifysaver.spotlog import get_logger


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
        self.logger = get_logger(f"{self.__class__.__name__}")
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.searcher = YoutubeMusicSearcher()
        self.lrc_client = LrclibAPI()
        self.image_downloader = ImageDownloader()

    @staticmethod
    def string_to_audio_format(format_str: str) -> AudioFormat:
        """Convert string format to AudioFormat enum.

        Args:
            format_str: String format ("m4a", "mp3", "opus")

        Returns:
            AudioFormat enum value

        Raises:
            ValueError: If format string is not supported
        """
        format_map = {
            "m4a": AudioFormat.M4A,
            "mp3": AudioFormat.MP3,
            "opus": AudioFormat.OPUS,
        }

        if format_str.lower() not in format_map:
            raise ValueError(
                f"Unsupported format: {format_str}. Supported formats: {list(format_map.keys())}"
            )

        return format_map[format_str.lower()]

    @staticmethod
    def int_to_bitrate(bitrate_int: int) -> Bitrate:
        """Convert integer bitrate to Bitrate enum.

        Args:
            bitrate_int: Integer bitrate (96, 128, 192, 256)

        Returns:
            Bitrate enum value

        Raises:
            ValueError: If bitrate is not supported
        """
        bitrate_map = {
            96: Bitrate.B96,
            128: Bitrate.B128,
            192: Bitrate.B192,
            256: Bitrate.B256,
        }

        if bitrate_int not in bitrate_map:
            raise ValueError(
                f"Unsupported bitrate: {bitrate_int}. Supported bitrates: {list(bitrate_map.keys())}"
            )

        return bitrate_map[bitrate_int]

    def _get_ydl_opts(
        self,
        output_path: Path,
        output_format: AudioFormat = AudioFormat.M4A,
        bitrate: Bitrate = Bitrate.B128,
    ) -> dict:
        """Get robust yt-dlp configuration with cookie support.

        Args:
            output_path: Path where the file should be saved
            output_format: Audio format enum (M4A, MP3, OPUS). Default: M4A.
            bitrate: Bitrate enum (B96, B128, B192, B256). Default: B128.

        Returns:
            dict: yt-dlp configuration options
        """
        is_verbose = self.logger.getEffectiveLevel() <= logging.DEBUG
        ytm_base_url = "https://music.youtube.com"

        # Use enum values instead of hardcoded validation
        format_value = output_format.value
        bitrate_value = bitrate.value

        opts = {
            "format": "bestaudio/best",
            "outtmpl": str(output_path.with_suffix(f".%(ext)s")),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": format_value,
                    "preferredquality": str(bitrate_value),
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
                    "player_client": ["android"],
                    "player_skip": ["configs"],
                }
            },
            "retries": 5,
            "fragment_retries": 5,
            "skip_unavailable_fragments": True,
            "allow_unplayable_formats": True,
            "force_keyframes_at_cuts": True,
        }

        return opts

    def _get_ydl_logger(self):
        """Create a yt-dlp logger that integrates with the application logger.

        Returns:
            YDLLogger: Custom logger for yt-dlp integration
        """
        from spotifysaver.spotlog import YDLLogger
        return YDLLogger()

    def _get_output_path(
        self,
        track: Track,
        album_artist: str = None,
        output_format: AudioFormat = AudioFormat.M4A,
    ) -> Path:
        """Generate output paths: Music/Artist/Album (Year)/Track.m4a.

        Args:
            track: Track object containing metadata
            album_artist: Artist name for album organization
            output_format: Audio format enum

        Returns:
            Path: Complete file path where the track should be saved
        """
        if track.source_type == "playlist":
            playlist_name = self._sanitize_filename(
                track.playlist_name or "Unknown Playlist"
            )
            dir_path = self.base_dir / playlist_name
        else:
            artist_name = (
                album_artist or track.artists[0] if track.artists else "Unknown Artist"
            )
            artist_name = self._sanitize_filename(artist_name)
            album_name = self._sanitize_filename(track.album_name or "Unknown Album")
            year = track.release_date[:4] if track.release_date else "Unknown"
            dir_path = self.base_dir / artist_name / f"{album_name} ({year})"

        dir_path.mkdir(parents=True, exist_ok=True)
        track_name = self._sanitize_filename(track.name or "Unknown Track")
        return dir_path / f"{track_name}.{output_format.value}"

    def _download_cover(self, track: Track) -> Optional[bytes]:
        """Download cover art from Spotify.

        Args:
            track: Track object containing cover URL

        Returns:
            bytes: Cover art image data, or None if download failed
        """
        if not track.cover_url:
            return None
        return self.image_downloader.get_image_from_url(track.cover_url)

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
                self.logger.info(f"Lyrics saved in: {lrc_path}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error saving song lyrics: {str(e)}", exc_info=True)
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

    def _save_artist_cover(self, url: str):
        """Download and save artist cover art.

        Args:
            url: URL of the cover image
        """
        if not url:
            return

        output_path = self.base_dir / "folder.jpg"
        try:
            image = self.image_downloader.download_image(url, output_path)
            if image:
                self.logger.info(f"Artist cover saved in: {output_path}")
        except Exception as e:
            self.logger.error(f"Error downloading artist cover: {e}")

    def _save_cover_album(self, url: str, output_path: Path):
        """Download and save album cover art.

        Args:
            url: URL of the cover image
            output_path: Path where the cover should be saved
        """
        if not url:
            return

        try:
            image = self.image_downloader.download_image(url, output_path)
            if image:
                self.logger.info(f"Cover saved in: {output_path}")
        except Exception as e:
            self.logger.error(f"Error downloading cover: {e}")

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for Windows compatibility.

        Args:
            filename: Original filename

        Returns:
            str: Sanitized filename safe for Windows
        """
        # Replace problematic characters
        filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

        # Replace em dash and en dash with regular dash
        filename = filename.replace("–", "-").replace("—", "-")

        # Remove multiple spaces and replace with single space
        filename = re.sub(r"\s+", " ", filename)

        # Trim whitespace and dots from start/end
        filename = filename.strip(". ")

        # Limit length to 200 characters to avoid Windows path limits
        if len(filename) > 200:
            filename = filename[:200].strip()

        return filename

    def download_track(
        self,
        track: Track,
        output_format: AudioFormat = AudioFormat.M4A,
        bitrate: Bitrate = Bitrate.B128,
        album_artist: str = None,
        download_lyrics: bool = False,
    ) -> tuple[Optional[Path], Optional[Track]]:
        """Download a track from YouTube Music with Spotify metadata.

        Args:
            track: Track object with metadata
            yt_url: YouTube Music URL for the track
            album_artist: Artist name for file organization
            download_lyrics: Whether to download lyrics
            output_format: Audio format enum (M4A, MP3, OPUS).
            bitrate: Audio bitrate enum (B96, B128, B192, B256).

        Returns:
            tuple: (Downloaded file path, Updated track) or (None, None) on error
        """
        output_path = self._get_output_path(track, album_artist, output_format)
        yt_url = self.searcher.search_track(track)
        ydl_opts = self._get_ydl_opts(output_path, output_format, bitrate)

        if not yt_url:
            self.logger.error(f"No match found for: {track.name}")
            return None, None

        try:
            # 1. Descarga el audio
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([yt_url])

            # 2. Add metadata and cover art
            cover_data = self._download_cover(track)
            metadata = MusicFileMetadata(
                file_path=output_path, track=track, cover_data=cover_data
            )
            metadata.add_metadata()

            # 3. Lyrics handling
            updated_track = track
            if download_lyrics:
                success = self._save_lyrics(track, output_path)
                updated_track = track.with_lyrics_status(success)

            self.logger.info(f"Download completed: {output_path}")
            return output_path, updated_track

        except Exception as e:
            self.logger.error(f"Error downloading {track.name}: {e}", exc_info=True)
            if output_path.exists():
                self.logger.debug(f"Removing corrupt file: {output_path}")
                output_path.unlink()
            return None, None

    def download_album(
        self,
        album: Album,
        output_format: AudioFormat = AudioFormat.M4A,
        bitrate: Bitrate = Bitrate.B128,
        download_lyrics: bool = False,
        nfo: bool = False,
        cover: bool = False,
    ):
        """Download a complete album and generate metadata.

        Args:
            album: Album object to download
            output_format: Audio format enum
            bitrate: Audio bitrate enum
            download_lyrics: Whether to download lyrics for tracks
            nfo: Whether to generate NFO metadata file
            cover: Whether to download album cover
        """
        for track in album.tracks:
            self.download_track(
                track=track,
                output_format=output_format,
                bitrate=bitrate,
                album_artist=album.artists[0],
                download_lyrics=download_lyrics,
            )

        output_dir = self._get_album_dir(album)

        # Generar NFO después de descargar todos los tracks
        if nfo:
            self.logger.info(f"Generating NFO for album: {album.name}")
            NFOGenerator.generate(album, output_dir)

        # Download cover art
        if cover and album.cover_url:
            self.logger.info(f"Downloading cover for album: {album.name}")
            self._save_cover_album(album.cover_url, output_dir / "cover.jpg")

        pass

    def download_album_cli(
        self,
        album: Album,
        download_lyrics: bool = False,
        output_format: AudioFormat = AudioFormat.M4A,
        bitrate: Bitrate = Bitrate.B128,
        nfo: bool = False,  # Generate NFO
        cover: bool = False,  # Download cover art
        progress_callback: Optional[callable] = None,  # Progress callback
    ) -> tuple[int, int]:  # Returns (success, total)
        """Download a complete album with progress support.

        Args:
            album: Album object to download
            download_lyrics: Whether to download lyrics
            output_format: Audio format enum
            bitrate: Audio bitrate enum
            nfo: Whether to generate NFO file
            cover: Whether to download cover art
            progress_callback: Function that receives (current_track, total_tracks, track_name).
                            Example: lambda idx, total, name: print(f"{idx}/{total} {name}")

        Returns:
            tuple: (successful_downloads, total_tracks)
        """
        if not album.tracks:
            self.logger.error("Álbum no contiene tracks.")
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
                    track=track,
                    album_artist=album.artists[0],
                    download_lyrics=download_lyrics,
                    output_format=output_format,
                    bitrate=bitrate,
                )
                if audio_path:
                    success += 1
            except Exception as e:
                self.logger.error(f"Error en track {track.name}: {str(e)}")

        # Generar metadatos solo si hay éxitos
        if success > 0:
            output_dir = self._get_album_dir(album)
            if nfo:
                NFOGenerator.generate(album, output_dir)
            if cover and album.cover_url:
                self._save_cover_album(album.cover_url, output_dir / "cover.jpg")

            # Guarda el cover del artista
            # self._save_artist_cover()

        return success, len(album.tracks)

    def download_playlist(
        self,
        playlist: Playlist,
        output_format: AudioFormat = AudioFormat.M4A,
        bitrate: Bitrate = Bitrate.B128,
        download_lyrics: bool = False,
        cover: bool = False,
        nfo: bool = False,
    ):
        """Download a complete playlist and generate metadata.

        Args:
            playlist: Playlist object to download
            output_format: Audio format enum
            bitrate: Audio bitrate enum
            download_lyrics: Whether to download lyrics
            cover: Whether to download playlist cover
            nfo: Whether to generate NFO file

        Returns:
            bool: True if at least one track was successfully downloaded
        """

        # Validación básica
        if not playlist.name:
            self.logger.error("Playlist name is empty. Cannot create directory.")
            return False
        if not playlist.tracks:
            self.logger.warning(f"Playlist '{playlist.name}' has no tracks.")
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
                    track,
                    output_format=output_format,
                    bitrate=bitrate,
                    download_lyrics=download_lyrics,
                )
                if updated_track:
                    success = True
            except Exception as e:
                failed_tracks.append(track.name)
                self.logger.error(
                    f"Error downloading track {track.name}: {e}"
                )  # Download cover art (only if successful)
        if success and playlist.cover_url and cover:
            self.logger.info(f"Downloading cover for playlist: {playlist.name}")
            self._save_cover_album(playlist.cover_url, output_dir / "cover.jpg")

        # Generate NFO (only if successful)
        if success and nfo:
            self.logger.info(f"Generating NFO for playlist: {playlist.name}")
            NFOGenerator.generate(playlist, output_dir)

        # Log results
        if failed_tracks:
            self.logger.warning(
                f"Failed downloads in playlist '{playlist.name}': {len(failed_tracks)}/{len(playlist.tracks)}. "
                f"Ejemplos: {', '.join(failed_tracks[:3])}{'...' if len(failed_tracks) > 3 else ''}"
            )

        return success

    def download_playlist_cli(
        self,
        playlist: Playlist,
        output_format: AudioFormat = AudioFormat.M4A,
        bitrate: Bitrate = Bitrate.B128,
        download_lyrics: bool = False,
        cover: bool = False,
        progress_callback: Optional[callable] = None,
    ) -> tuple[int, int]:
        """Download a complete playlist with progress bar support.

        Args:
            playlist: Playlist object to download
            output_format: Audio format enum
            bitrate: Audio bitrate enum
            download_lyrics: Whether to download lyrics
            cover: Whether to download playlist cover
            progress_callback: Function that receives (current_track, total_tracks, track_name).
                            Example: lambda idx, total, name: print(f"{idx}/{total} {name}")

        Returns:
            tuple: (successful_downloads, total_tracks)
        """
        if not playlist.name or not playlist.tracks:
            self.logger.error("Playlist inválida: sin nombre o tracks vacíos")
            return 0, 0

        output_dir = self.base_dir / playlist.name
        output_dir.mkdir(parents=True, exist_ok=True)
        success = 0

        for idx, track in enumerate(playlist.tracks, 1):
            try:
                # Notificar progreso (si hay callback)
                if progress_callback:
                    progress_callback(idx, len(playlist.tracks), track.name)

                _, updated_track = self.download_track(
                    track,
                    output_format=output_format,
                    bitrate=bitrate,
                    download_lyrics=download_lyrics,
                )
                if updated_track:
                    success += 1
            except Exception as e:
                self.logger.error(f"Error en {track.name}: {str(e)}")

        if success > 0 and cover and playlist.cover_url:
            try:
                self._save_cover_album(playlist.cover_url, output_dir / "cover.jpg")
            except Exception as e:
                self.logger.error(f"Error downloading playlist cover: {str(e)}")

        return success, len(playlist.tracks)
