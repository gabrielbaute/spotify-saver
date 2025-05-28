from ytmusicapi import YTMusic
from typing import List, Dict, Optional
from functools import lru_cache
from src.models.track import Track
from src.spotlog import get_logger

logger = get_logger("YouTubeMusicSearcher")

class YoutubeMusicSearcher:
    def __init__(self):
        self.ytmusic = YTMusic()
        self.max_retries = 3

    @staticmethod
    def _similar(a: str, b: str) -> float:
        """Calcula similitud entre strings (0-1) usando SequenceMatcher."""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, a, b).ratio()

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalización consistente para textos."""
        text = (text.lower()
                .replace("official", "")
                .replace("video", "")
                .translate(str.maketrans('', '', '()[]-')))
        return ' '.join([w for w in text.split() if w not in {"lyrics", "audio"}])

    def _is_valid_match(self, yt_result: Dict, spotify_track: Track) -> bool:
        """Valida coincidencias con umbrales dinámicos."""
        # Umbrales dinámicos
        title_words = len(spotify_track.name.split())
        title_threshold = max(0.75 - (0.03 * (title_words - 3)), 0.6)
        artist_threshold = min(0.7 + (0.05 * len(spotify_track.artists[0].split())), 0.85)

        # Preparación de datos
        yt_title = self._normalize(yt_result.get('title', ''))
        sp_title = self._normalize(spotify_track.name)
        yt_artists = [self._normalize(a['name']) for a in yt_result.get('artists', [])]
        sp_artists = [self._normalize(a) for a in spotify_track.artists]

        # Validación
        duration_ok = abs(yt_result.get('duration_seconds', 0) - spotify_track.duration) <= 3
        title_ok = self._similar(yt_title, sp_title) >= title_threshold
        artist_ok = any(
            self._similar(yt_artist, sp_artist) >= artist_threshold
            for yt_artist in yt_artists
            for sp_artist in sp_artists
        )

        # Debug logging
        logger.debug(f"""
        Match evaluation for '{yt_title}':
        - Title similarity: {self._similar(yt_title, sp_title):.2f} (threshold: {title_threshold:.2f})
        - Artist similarity: {max(self._similar(a, b) for a in yt_artists for b in sp_artists):.2f} (threshold: {artist_threshold:.2f})
        - Duration diff: {abs(yt_result.get('duration_seconds', 0) - spotify_track.duration)}s
        """)

        return duration_ok and title_ok and artist_ok

    def _search_individual_track(self, track: Track) -> Optional[str]:
        """Búsqueda estándar de track individual."""
        queries = [
            f"{track.artists[0]} {track.name} {track.album_name}",
            f"{track.artists[0]} {track.name}",
            f"{track.name} {track.artists[0]}",
            track.name
        ]
        
        for query in queries:
            try:
                results = self.ytmusic.search(
                    query=query,
                    filter="songs",
                    limit=10
                )
                
                # Ordenar por mejor coincidencia de duración primero
                results.sort(
                    key=lambda x: abs(x.get('duration_seconds', 0) - track.duration)
                )
                
                for result in results:
                    if self._is_valid_match(result, track):
                        logger.info(f"Found valid match: {result['title']}")
                        return f"https://music.youtube.com/watch?v={result['videoId']}"
                        
            except Exception as e:
                logger.error(f"Search error for '{query}': {e}")
        
        return None

    def _search_via_album(self, track: Track) -> Optional[str]:
        """Busca el track dentro del álbum completo."""
        try:
            # Búsqueda del álbum
            album_results = self.ytmusic.search(
                query=f"{track.album_name} {track.artists[0]}",
                filter="albums",
                limit=3
            )
            
            if not album_results:
                return None

            # Obtener tracks del álbum
            album = self.ytmusic.get_album(album_results[0]['browseId'])
            for yt_track in album['tracks']:
                if self._is_valid_match(yt_track, track):
                    logger.info(f"Found via album: {yt_track['title']}")
                    return f"https://music.youtube.com/watch?v={yt_track['videoId']}"
                    
        except Exception as e:
            logger.error(f"Album search error: {e}")
        
        return None

    @lru_cache(maxsize=100)
    def search_track(self, track: Track) -> Optional[str]:
        """Búsqueda con sistema de fallback integrado."""
        # Primero intenta búsqueda individual
        if url := self._search_individual_track(track):
            return url
            
        # Fallback a búsqueda por álbum
        logger.info(f"Trying album fallback for: {track.name}")
        return self._search_via_album(track)
