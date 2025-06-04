"""Configures environment settings for the application."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carga el .env desde la raíz del proyecto (ajusta según tu estructura)
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

class Config:
    """Configuration class for Spotify API and other settings."""
    
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")

    # Logger
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()

    # Youtube cookie file
    YTDLP_COOKIES_PATH = os.getenv("YTDLP_COOKIES_PATH", None)

    @classmethod
    def validate(cls):
        """Verifica que las variables críticas estén configuradas."""
        if not cls.SPOTIFY_CLIENT_ID or not cls.SPOTIFY_CLIENT_SECRET:
            raise ValueError("Spotify API credentials missing in .env file")
