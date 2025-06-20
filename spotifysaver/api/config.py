"""API Configuration Settings"""

import os
from typing import List


class APIConfig:
    """Configuration settings for the FastAPI application."""

    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]

    # API settings
    DEFAULT_OUTPUT_DIR: str = "Music"
    MAX_CONCURRENT_DOWNLOADS: int = 3

    # File settings
    ALLOWED_FORMATS: List[str] = ["m4a", "mp3"]
    DEFAULT_FORMAT: str = "m4a"

    # Service settings
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "info"

    @classmethod
    def get_output_dir(cls) -> str:
        """Get the output directory from environment or default."""
        return os.getenv("SPOTIFYSAVER_OUTPUT_DIR", cls.DEFAULT_OUTPUT_DIR)
