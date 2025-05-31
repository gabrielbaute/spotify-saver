import requests
from typing import Optional, Dict
from src.models import Track
from src.spotlog import get_logger
from src.apis.errors.errors import APIError

logger = get_logger("LrclibAPI")

class LrclibAPI:
    BASE_URL = "https://lrclib.net/api"
    
    def __init__(self):
        """Inicializa el cliente de LRC Lib API."""
        self.session = requests.Session()
        self.session.timeout = 10  # 10 segundos de timeout

    def get_lyrics(self, track: Track, synced: bool = True) -> Optional[str]:
        """
        Obtiene letras sincronizadas o planas para un track.
        
        Args:
            track: Objeto Track con los metadatos
            synced: Si True, devuelve letras sincronizadas (.lrc)
        
        Returns:
            str: Letras en formato solicitado o None si hay error
        """
        try:
            params = {
                "track_name": track.name,
                "artist_name": track.artists[0],
                "album_name": track.album_name,
                "duration": int(track.duration)
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/get",
                params=params,
                headers={"Accept": "application/json"}
            )
            
            if response.status_code == 404:
                logger.debug(f"Lyrics not found for: {track.name}")
                return None
                
            response.raise_for_status()
            data = response.json()
            
            lyric_type = "syncedLyrics" if synced else "plainLyrics"
            logger.info(f"Song lyrics obtained: {lyric_type}")
            return data.get(lyric_type)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in the LRC Lib API: {str(e)}")
            raise APIError(f"LRC Lib API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise APIError(f"Unexpected error: {str(e)}")

    def get_lyrics_with_fallback(self, track: Track) -> Optional[str]:
        """Intenta obtener letras sincronizadas, si falla usa las planas"""
        try:
            return self.get_lyrics(track, synced=True) or self.get_lyrics(track, synced=False)
        except APIError:
            return None
