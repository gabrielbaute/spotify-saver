"""Custom exception classes for API errors in Spotify Saver.

This module defines custom exception classes for handling various types of API
errors that can occur when interacting with external services like Spotify,
YouTube Music, and LRC Lib.
"""


class APIError(Exception):
    """Base exception class for all API-related errors.
    
    This is the parent class for all API exceptions in the application.
    It provides a common interface for error handling with optional status codes.
    
    Attributes:
        status_code: HTTP status code associated with the error (if applicable)
    """

    def __init__(self, message: str, status_code: int = None):
        """Initialize the APIError with a message and optional status code.
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code (optional)
        """
        self.status_code = status_code
        super().__init__(message)


class SpotifyAPIError(APIError):
    """Exception for Spotify Web API specific errors.
    
    Raised when errors occur while interacting with the Spotify Web API,
    such as authentication failures, invalid requests, or service unavailability.
    """


class YouTubeAPIError(APIError):
    """Exception for YouTube Music API specific errors.
    
    Raised when errors occur while searching or downloading from YouTube Music,
    including search failures, download errors, or API quota exceeded.
    """


class RateLimitExceeded(APIError):
    """Exception for HTTP 429 Too Many Requests errors.
    
    Raised when API rate limits are exceeded for any service. Includes
    information about which service triggered the limit and retry timing.
    """

    def __init__(self, service: str, retry_after: int = None):
        """Initialize rate limit exception with service and retry information.
        
        Args:
            service: Name of the service that triggered the rate limit
            retry_after: Suggested retry delay in seconds (optional)
        """
        message = f"Rate limit exceeded for {service}"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message, 429)


class AlbumNotFoundError(APIError):
    """Exception raised when a requested album cannot be found.
    
    This error occurs when trying to fetch album data that doesn't exist
    or is not accessible through the API.
    """

    pass


class InvalidResultError(APIError):
    """Exception raised when API returns unexpected or malformed data.
    
    This error occurs when the API response doesn't match the expected format
    or contains invalid data that cannot be processed.
    """

    pass
