from ytmusicapi import YTMusic
from typing import List, Dict, Optional, Tuple
from functools import lru_cache

from spotifysaver.models.track import Track
from spotifysaver.spotlog import get_logger
from spotifysaver.apis.errors.errors import YouTubeAPIError, AlbumNotFoundError, InvalidResultError

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

    def _search_with_fallback(self, track: Track) -> Optional[str]:
        """Estrategia de búsqueda priorizada."""
        search_strategies = [
            self._search_exact_match,
            self._search_album_context,
            self._search_fuzzy_match
        ]
        
        for strategy in search_strategies:
            if url := strategy(track):
                logger.info(f"Found track: {track.name} by {track.artists[0]} using {strategy.__name__}")
                return url
        logger.warning(f"No results found for {track.name} by {track.artists[0]}")
        return None

    def _search_exact_match(self, track: Track) -> Optional[str]:
        """Búsqueda exacta con filtro de canciones."""
        query = f"{track.artists[0]} {track.name} {track.album_name}"
        results = self.ytmusic.search(
            query=query,
            filter="songs",
            limit=5,
            ignore_spelling=True
        )
        logger.debug(f"Exact match search results: {results}")
        return self._process_results(results, track, strict=True)

    def _search_album_context(self, track: Track) -> Optional[str]:
        """Busca el álbum con manejo de errores detallado."""
        try:
            # Búsqueda del álbum
            album_results = self.ytmusic.search(
                query=f"{track.album_name} {track.artists[0]}",
                filter="albums",
                limit=1
            )
            
            if not album_results:
                raise AlbumNotFoundError(f"Album '{track.album_name}' not found")
            
            # Verificación de tipo
            if not isinstance(album_results[0], dict) or 'browseId' not in album_results[0]:
                raise InvalidResultError("Invalid album search result format")
            
            # Obtención de tracks
            album_tracks = self.ytmusic.get_album(album_results[0]['browseId']).get('tracks', [])
            
            if not album_tracks:
                raise AlbumNotFoundError(f"No tracks found in album '{track.album_name}'")
            
            return self._process_results(album_tracks, track, strict=False)
            
        except YouTubeAPIError:
            raise
        except Exception as e:
            raise InvalidResultError(f"Unexpected error in album search: {str(e)}")


    def _search_fuzzy_match(self, track: Track) -> Optional[str]:
        """Búsqueda más flexible cuando las exactas fallan."""
        results = self.ytmusic.search(
            query=f"{track.artists[0]} {track.name}",
            filter="songs",
            limit=10,
            ignore_spelling=False  # Permite correcciones
        )
        return self._process_results(results, track, strict=False)

    def _process_results(self, results: List[Dict], track: Track, strict: bool) -> Optional[str]:
        """Evalúa y selecciona el mejor resultado."""
        if not results:
            logger.warning(f"No results found for {track.name} by {track.artists[0]}")
            return None

        scored_results = []
        for result in results:
            score = self._calculate_match_score(result, track, strict)
            logger.debug(f"Score for {result.get('title', 'Unknown')} is {score}")
            if score > 0:
                scored_results.append((score, result))
        
        if not scored_results:
            logger.warning(f"No valid matches found for {track.name} by {track.artists[0]}")
            return None
            
        # Ordena por puntaje descendente
        scored_results.sort(reverse=True, key=lambda x: x[0])
        best_match = scored_results[0][1]
        logger.info(f"Best match for {track.name} by {track.artists[0]}: {best_match.get('title', 'Unknown')} with score {scored_results[0][0]}")
        return f"https://music.youtube.com/watch?v={best_match['videoId']}"

    def _calculate_match_score(self, yt_result: Dict, track: Track, strict: bool) -> float:
        """Sistema de puntuación mejorado."""
        try:
            # 1. Coincidencia de duración (30% del score)
            duration_diff = abs(yt_result.get('duration_seconds', 0) - track.duration)
            duration_score = max(0, 1 - (duration_diff / 10))  # 1 si es exacto, 0 si >10s diff
            
            # 2. Coincidencia de artistas (40% del score)
            yt_artists = {a['name'].lower() for a in yt_result.get('artists', []) if isinstance(a, dict)}
            sp_artists = {a.lower() for a in track.artists}
            artist_overlap = len(yt_artists & sp_artists) / len(sp_artists)
            artist_score = artist_overlap * 0.4
            
            # 3. Coincidencia de título (30% del score)
            title_similarity = self._similar(
                str(yt_result.get('title', '')).lower(),
                track.name.lower()
            )
            title_score = title_similarity * 0.3
            
            # 4. Bonus por álbum (manejo seguro de tipos)
            bonus = 0
            album_data = yt_result.get('album')
            if album_data:
                album_name = album_data['name'].lower() if isinstance(album_data, dict) else str(album_data).lower()
                if track.album_name.lower() in album_name:
                    bonus += 0.1
            
            total_score = duration_score + artist_score + title_score + bonus
            return total_score if total_score >= (0.7 if strict else 0.6) else 0
        
        except Exception as e:
            logger.error(f"Error calculating score: {str(e)}")
            logger.debug(f"Problematic result: {yt_result}")
            return 0

    @lru_cache(maxsize=100)
    def search_track(self, track: Track) -> Optional[str]:
        """Búsqueda con manejo elegante de errores."""
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                return self._search_with_fallback(track)
                
            except AlbumNotFoundError as e:
                logger.warning(f"Attempt {attempt}: {str(e)}")
                last_error = e
            except InvalidResultError as e:
                logger.error(f"Attempt {attempt}: Invalid API response - {str(e)}")
                last_error = e
            except Exception as e:
                logger.error(f"Attempt {attempt}: Unexpected error - {str(e)}")
                last_error = e
                
        logger.error(f"All attempts failed for '{track.name}'")
        if last_error:
            logger.info(f"Last error details: {str(last_error)}")
        return None


