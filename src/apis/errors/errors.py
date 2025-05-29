class YouTubeMatchError(Exception):
    """Base exception for YouTube matching errors"""
    pass

class AlbumNotFoundError(YouTubeMatchError):
    """When the album can't be found"""
    pass

class InvalidResultError(YouTubeMatchError):
    """When the API returns unexpected data"""
    pass
