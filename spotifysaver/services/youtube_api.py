"""YouTube Music Searcher Service"""

from functools import lru_cache
from typing import List, Dict, Optional, Tuple

from ytmusicapi import YTMusic

from spotifysaver.models.track import Track
from spotifysaver.spotlog import get_logger
from spotifysaver.services.score_match_calculator import ScoreMatchCalculator
from spotifysaver.services.errors.errors import (
    YouTubeAPIError,
    AlbumNotFoundError,
    InvalidResultError,
)


class YoutubeMusicSearcher:
    """YouTube Music search service for finding tracks.
    
    This class provides functionality to search for tracks on YouTube Music
    using various strategies and scoring algorithms to find the best matches
    for Spotify tracks.
    
    Attributes:
        ytmusic: YTMusic API client instance
        max_retries: Maximum number of retry attempts for failed searches
    """
    
    def __init__(self):
        """Initialize the YouTube Music searcher.
        
        Sets up the YTMusic client and configures retry behavior.
        """
        self.ytmusic = YTMusic()
        self.scorer = ScoreMatchCalculator()
        self.max_retries = 3
        self.logger = get_logger(f"{self.__class__.__name__}")

    @staticmethod
    def _similar(a: str, b: str) -> float:
        """Calculate similarity between strings (0-1) using SequenceMatcher.
        
        Args:
            a: First string to compare
            b: Second string to compare
            
        Returns:
            float: Similarity ratio between 0.0 and 1.0
        """
        from difflib import SequenceMatcher

        return SequenceMatcher(None, a, b).ratio()

    @staticmethod
    def _normalize(text: str) -> str:
        """Consistent text normalization for comparison.
        
        Removes common words and characters that might interfere with matching.
        
        Args:
            text: Text to normalize
            
        Returns:
            str: Normalized text string
        """
        text = (
            text.lower()
            .replace("official", "")
            .replace("video", "")
            .translate(str.maketrans("", "", "()[]-"))
        )
        return " ".join([w for w in text.split() if w not in {"lyrics", "audio"}])

    def _search_with_fallback(self, track: Track) -> Optional[str]:
        """Prioritized search strategy with multiple fallback methods.
        
        Tries different search strategies in order of reliability until
        a match is found.
        
        Args:
            track: Track object to search for
            
        Returns:
            str: YouTube Music URL if found, None otherwise
        """
        search_strategies = [
            self._search_exact_match,
            self._search_album_context,
            self._search_fuzzy_match,
        ]

        for strategy in search_strategies:
            if url := strategy(track):
                self.logger.info(
                    f"Found track: {track.name} by {track.artists[0]} using {strategy.__name__}"
                )
                return url
        self.logger.warning(f"No results found for {track.name} by {track.artists[0]}")
        return None

    def _search_exact_match(self, track: Track) -> Optional[str]:
        """Exact search with song filter.
        
        Args:
            track: Track object to search for
            
        Returns:
            str: YouTube Music URL if found, None otherwise
        """
        query = self._normalize(f"{track.artists[0]} {track.name} {track.album_name}")
        results = self.ytmusic.search(
            query=query,
            filter="songs",
            limit=5,
            ignore_spelling=True
        )
        self.logger.debug(f"Exact match search results: {results}")
        return self._process_results(results, track, strict=True)

    def _search_album_context(self, track: Track) -> Optional[str]:
        """Search for the album with detailed error handling.
        
        Args:
            track: Track object to search for
            
        Returns:
            str: YouTube Music URL if found, None otherwise
            
        Raises:
            AlbumNotFoundError: If the album cannot be found
            InvalidResultError: If the API returns invalid data
        """
        try:
            # Búsqueda del álbum
            album_results = self.ytmusic.search(
                query=self._normalize(f"{track.artists[0]} {track.name} {track.album_name}"),
                filter="albums",
                limit=1
            )

            if not album_results:
                raise AlbumNotFoundError(f"Album '{track.album_name}' not found")

            # Verificación de tipo
            if (
                not isinstance(album_results[0], dict)
                or "browseId" not in album_results[0]
            ):
                raise InvalidResultError("Invalid album search result format")

            # Obtención de tracks
            album_tracks = self.ytmusic.get_album(album_results[0]["browseId"]).get(
                "tracks", []
            )

            if not album_tracks:
                raise AlbumNotFoundError(
                    f"No tracks found in album '{track.album_name}'"
                )

            return self._process_results(album_tracks, track, strict=False)

        except YouTubeAPIError:
            raise
        except Exception as e:
            raise InvalidResultError(f"Unexpected error in album search: {str(e)}")

    def _search_fuzzy_match(self, track: Track) -> Optional[str]:
        """More flexible search when exact searches fail.
        
        Args:
            track: Track object to search for
            
        Returns:
            str: YouTube Music URL if found, None otherwise
        """
        results = self.ytmusic.search(
            query=self._normalize(f"{track.artists[0]} {track.name} {track.album_name}"),
            filter="songs",
            limit=10,
            ignore_spelling=False,  # Allow spelling corrections
        )
        return self._process_results(results, track, strict=False)

    def _process_results(
        self, results: List[Dict], track: Track, strict: bool
    ) -> Optional[str]:
        """Evaluate and select the best result.
        
        Args:
            results: List of search results from YouTube Music
            track: Original track to match against
            strict: Whether to use strict matching criteria
            
        Returns:
            str: YouTube Music URL of the best match, None if no valid matches
        """
        if not results:
            self.logger.warning(f"No results found for {track.name} by {track.artists[0]}")
            return None

        scored_results = []
        for result in results:
            score = self.scorer._calculate_match_score(result, track, strict)
            self.logger.debug(f"Score for {result.get('title', 'Unknown')} is {score}")
            if score > 0:
                scored_results.append((score, result))

        if not scored_results:
            self.logger.warning(f"No valid matches found for {track.name} by {track.artists[0]}")
            return None

        scored_results.sort(reverse=True, key=lambda x: x[0])
        best_match = scored_results[0][1]
        self.logger.info(
            f"Best match for {track.name} by {track.artists[0]}: {best_match.get('title', 'Unknown')} with score {scored_results[0][0]}"
        )
        return f"https://music.youtube.com/watch?v={best_match['videoId']}"

    @lru_cache(maxsize=100)
    def search_track(self, track: Track) -> Optional[str]:
        """Search for a track with elegant error handling.
        
        Main entry point for track searching with retry logic and caching.
        
        Args:
            track: Track object to search for
            
        Returns:
            str: YouTube Music URL if found, None if not found after all attempts
        """
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                return self._search_with_fallback(track)

            except AlbumNotFoundError as e:
                self.logger.warning(f"Attempt {attempt}: {str(e)}")
                last_error = e
            except InvalidResultError as e:
                self.logger.error(f"Attempt {attempt}: Invalid API response - {str(e)}")
                last_error = e
            except Exception as e:
                self.logger.error(f"Attempt {attempt}: Unexpected error - {str(e)}")
                last_error = e

        self.logger.error(f"All attempts failed for '{track.name}'")
        if last_error:
            self.logger.info(f"Last error details: {str(last_error)}")
        return None
