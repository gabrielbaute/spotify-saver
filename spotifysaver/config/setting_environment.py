"""Application configuration module for environment settings and validation.

This module handles loading environment variables from .env files and provides
configuration settings for the SpotifySaver application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (adjust according to your structure)
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)


class Config:
    """Configuration class for managing application settings.
    
    This class loads and manages configuration settings from environment variables,
    including Spotify API credentials, logging levels, and YouTube download settings.
    
    Attributes:
        SPOTIFY_CLIENT_ID: Spotify API client ID from environment
        SPOTIFY_CLIENT_SECRET: Spotify API client secret from environment  
        SPOTIFY_REDIRECT_URI: OAuth redirect URI for Spotify authentication
        LOG_LEVEL: Application logging level (default: 'info')
        YTDLP_COOKIES_PATH: Path to YouTube Music cookies file for age-restricted content
    """

    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI = os.getenv(
        "SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback"
    )

    # Logger configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()

    # YouTube cookies file for bypassing age restrictions
    YTDLP_COOKIES_PATH = os.getenv("YTDLP_COOKIES_PATH", None)

    @classmethod
    def validate(cls):
        """Validate that critical environment variables are configured.
        
        Raises:
            ValueError: If required Spotify API credentials are missing
        """
        if not cls.SPOTIFY_CLIENT_ID or not cls.SPOTIFY_CLIENT_SECRET:
            raise ValueError("Spotify API credentials missing in .env file")
