"""Configures environment settings for the application."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carga el .env desde la raíz del proyecto (ajusta según tu estructura)
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

class Config:
    """Configuration class for Spotify API and other settings."""
    
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_DLP_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_DLP_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_DLP_REDIRECT_URI", "http://localhost:8888/callback")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()

    @classmethod
    def validate(cls):
        """Verifica que las variables críticas estén configuradas."""
        if not cls.SPOTIFY_CLIENT_ID or not cls.SPOTIFY_CLIENT_SECRET:
            raise ValueError("Spotify API credentials missing in .env file")
