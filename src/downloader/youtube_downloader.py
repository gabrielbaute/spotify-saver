import yt_dlp
import requests
import logging
from pathlib import Path
from typing import Optional
from mutagen.mp4 import MP4, MP4Cover

from src.apis import YoutubeMusicSearcher, LrclibAPI
from src.metadata import NFOGenerator
from src.models import Track, Album
from src.config import Config
from src.spotlog import get_logger

logger = get_logger("YoutubeDownloader")

class YouTubeDownloader:
    """Descarga tracks de YouTube Music y añade metadatos de Spotify."""

    def __init__(self, base_dir: str = "Music"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.searcher = YoutubeMusicSearcher()
        self.lrc_client = LrclibAPI()

    def _get_ydl_opts(self, output_path: Path) -> dict:
        """Configuración robusta para yt-dlp con soporte para cookies"""
        is_verbose = logger.getEffectiveLevel() <= logging.DEBUG
        ytm_base_url = "https://music.youtube.com"
        
        opts = {
            "format": "m4a/bestaudio[abr<=128]/best",
            "outtmpl": str(output_path.with_suffix(".%(ext)s")),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }],
            "quiet": not is_verbose,
            "verbose": is_verbose,
            "extract_flat": False,
            "logger": self._get_ydl_logger(),
            # Parámetros de cookies y headers para evitar bloqueos
            "cookiefile": str(Config.YTDLP_COOKIES_PATH) if Config.YTDLP_COOKIES_PATH else None,
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
        """Logger de yt-dlp."""
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

    def _get_output_path(self, track: Track) -> Path:
        """Genera rutas: Music/Artist/Album (Year)/Track.m4a."""
        artist_dir = self.base_dir / track.artists[0]
        album_dir = artist_dir / f"{track.album_name} ({track.release_date[:4]})"
        album_dir.mkdir(parents=True, exist_ok=True)
        return album_dir / f"{track.name}.m4a"

    def _download_cover(self, track: Track) -> Optional[bytes]:
        """Descarga la portada desde Spotify."""
        if not track.cover_url:
            return None
        try:
            response = requests.get(track.cover_url, timeout=10)
            return response.content if response.status_code == 200 else None
        except Exception as e:
            logger.error(f"Error downloading cover: {e}")
            return None

    def _add_metadata(self, file_path: Path, track: Track, cover_data: Optional[bytes]):
        """Añade metadatos y portada usando la API moderna de Mutagen."""
        try:
            audio = MP4(file_path)
            
            # Metadatos básicos (usando claves estándar MP4)
            audio["\xa9nam"] = [track.name]  # Título (¡Debe ser una lista!)
            audio["\xa9ART"] = [", ".join(track.artists)]  # Artista
            audio["\xa9alb"] = [track.album_name]  # Álbum
            audio["\xa9day"] = [track.release_date[:4]]  # Solo el año
            audio["\xa9gen"] = [", ".join(track.genres)] if track.genres else []  # Género
            audio["trkn"] = [(track.number, track.total_tracks)]  # Número de pista y total
            audio["disk"] = [(track.disc_number, 1)]  # Número de disco (asumiendo 1 disco)
            
            # Género (si existe en el track)
            if hasattr(track, "genres") and track.genres:
                audio["\xa9gen"] = [", ".join(track.genres)]
            
            # Portada
            if cover_data:
                audio["covr"] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]
            
            audio.save()
            logger.info(f"Metadata added to {file_path}")
        
        except Exception as e:
            logger.error(f"Error adding metadata: {str(e)}")
            raise

    def _save_lyrics(self, track: 'Track', audio_path: Path) -> bool:
        """Guarda letras sincronizadas como archivo .lrc"""
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

    def _get_album_dir(self, album: 'Album') -> Path:
        """Obtiene la ruta del directorio del álbum"""
        artist_dir = self.base_dir / album.artists[0]
        return artist_dir / f"{album.name} ({album.release_date[:4]})"
    
    def _save_cover_album(self, url: str, output_path: Path):
        """Descarga la portada del álbum"""
        if not url:
            return
            
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                output_path.write_bytes(response.content)
        except Exception as e:
            logger.error(f"Error downloading cover: {e}")

    def download_track(self, track: Track, yt_url: str, download_lyrics: bool = False) -> tuple[Optional[Path], Optional[Track]]:
        """
        Descarga un track desde YouTube Music con metadata de Spotify.
        
        Returns:
            tuple: (Path del archivo descargado, Track actualizado) o (None, None) en caso de error
        """
        output_path = self._get_output_path(track)
        yt_url = self.searcher.search_track(track)
        ydl_opts = self._get_ydl_opts(output_path)
        
        if not yt_url:
            logger.error(f"No match found for: {track.name}")
            return None, None

        try:
            # 1. Descarga el audio
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([yt_url])
            
            # 2. Añade metadatos y portada
            cover_data = self._download_cover(track)
            self._add_metadata(output_path, track, cover_data)

            # 3. Manejo de letras
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
    
    def download_album(self, album: Album, download_lyrics: bool = False):
        """Descarga un álbum completo y genera metadatos"""
        for track in album.tracks:
            self.download_track(track, download_lyrics=download_lyrics)
        
        # Generar NFO después de descargar todos los tracks
        output_dir = self._get_album_dir(album)
        NFOGenerator.generate(album, output_dir)

        # Descargar portada (opcional)
        self._save_cover_album(album.cover_url, output_dir / "cover.jpg")
        pass
