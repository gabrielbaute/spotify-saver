class APIError(Exception):
    """Base class for API exceptions"""
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message)

class SpotifyAPIError(APIError):
    """Spotify-specific API errors"""
    
class YouTubeAPIError(APIError):
    """YouTube Music API errors"""

class RateLimitExceeded(APIError):
    """429 Too Many Requests"""
    def __init__(self, service: str, retry_after: int = None):
        message = f"Rate limit exceeded for {service}"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message, 429)

class AlbumNotFoundError(APIError):
    """When the album can't be found"""
    pass

class InvalidResultError(APIError):
    """When the API returns unexpected data"""
    pass
