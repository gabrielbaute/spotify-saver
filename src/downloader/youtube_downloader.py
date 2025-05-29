import yt_dlp
import requests
import logging
from pathlib import Path
from typing import Optional
from mutagen.mp4 import MP4, MP4Cover

from src.apis import YoutubeMusicSearcher
from src.models import Track
from src.spotlog import get_logger

logger = get_logger("YoutubeDownloader")

class YouTubeDownloader:
    """Descarga tracks de YouTube Music y añade metadatos de Spotify."""

    def __init__(self, base_dir: str = "Music"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.searcher = YoutubeMusicSearcher()

    def _get_ydl_opts(self, output_path: Path) -> dict:
        """Genera opciones para yt-dlp basadas en el nivel de logging."""
        is_verbose = logger.getEffectiveLevel() <= logging.DEBUG
        
        return {
            "format": "m4a/bestaudio[abr<=128]/best",
            "outtmpl": str(output_path.with_suffix(".%(ext)s")),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }],
            "quiet": not is_verbose,  # Silencioso a menos que estemos en DEBUG
            "verbose": is_verbose,   # Output detallado solo en DEBUG
            "extract_flat": False,
            "logger": self._get_ydl_logger()  # Logger personalizado
        }

    def _get_ydl_logger(self):
        """Crea un logger adaptado para yt-dlp."""
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
            
            # Género (si existe en el track)
            if hasattr(track, "genres") and track.genres:
                audio["\xa9gen"] = [", ".join(track.genres)]
            
            # Portada (¡API nueva!)
            if cover_data:
                audio["covr"] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]
            
            audio.save()  # Guarda los cambios
            logger.info(f"Metadatos añadidos a {file_path}")
        
        except Exception as e:
            logger.error(f"Error añadiendo metadatos: {str(e)}")
            raise  # Opcional: relanza el error si quieres manejo externo


    def download_track(self, track: Track, yt_url: str) -> Optional[Path]:
        """Descarga un track desde YouTube Music con metadata de Spotify."""
        output_path = self._get_output_path(track)
        yt_url = self.searcher.search_track(track)
        ydl_opts = self._get_ydl_opts(output_path)
        
        if not yt_url:
            logger.error(f"No se encontró match para: {track.name}")
            return None

        try:
            # Descarga el audio
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([yt_url])

            # Añade metadatos y portada
            cover_data = self._download_cover(track)
            self._add_metadata(output_path, track, cover_data)

            logger.info(f"Download completed: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error downloading {track.name}: {e}")
            if output_path.exists():
                logger.debug(f"Removing corrupt file: {output_path}")
                output_path.unlink()  # Elimina archivo corrupto
            return None

