import yt_dlp
import requests
import logging
from pathlib import Path
from typing import Optional
from mutagen.mp4 import MP4, MP4Cover

from src.apis import YoutubeMusicSearcher, LrclibAPI
from src.models import Track
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
        """Oopciones para yt-dlp basadas en el nivel de logging."""
        is_verbose = logger.getEffectiveLevel() <= logging.DEBUG
        
        opts = {
            "format": "m4a/bestaudio[abr<=128]/best",
            "outtmpl": str(output_path.with_suffix(".%(ext)s")),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }],
            "quiet": not is_verbose,  # Silencioso a menos que estemos en DEBUG
            "verbose": is_verbose,   # Output detallado solo en DEBUG
            "extract_flat": False,
            "cookies": Config.YTDLP_COOKIES_PATH if Config.YTDLP_COOKIES_PATH else None,
            "logger": self._get_ydl_logger()
        }
        
        #if Config.YTDLP_COOKIES_PATH is not None:
        #    opts["cookiefile"] = str(Config.YTDLP_COOKIES_PATH) # Uso de cookies en caso de que existan
        #    logger.debug(f"Usando archivo de cookies desde: {Config.YTDLP_COOKIES_PATH}")
        
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

    def _save_lyrics(self, track: 'Track', audio_path: Path) -> bool:
        """Guarda letras sincronizadas como archivo .lrc"""
        try:
            lyrics = self.lrc_client.get_lyrics_with_fallback(track)
            if not lyrics or "[instrumental]" in lyrics.lower():
                return False
                
            lrc_path = audio_path.with_suffix(".lrc")
            lrc_path.write_text(lyrics, encoding="utf-8")

            if lrc_path.stat().st_size > 0:
                logger.info(f"Letras guardadas: {lrc_path}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error guardando letras: {str(e)}", exc_info=True)
            return False

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
            logger.error(f"No se encontró match para: {track.name}")
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
        