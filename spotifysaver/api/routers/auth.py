"""Spotify OAuth endpoints for the SpotifySaver API."""

from fastapi import APIRouter
from fastapi.responses import RedirectResponse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler

from ...config import Config
from ...spotlog import get_logger

logger = get_logger("auth")
router = APIRouter()

# Server-side state (single-user)
_server_token_info: dict = {}
_authenticated_user: dict = {}


def _get_auth_manager() -> SpotifyOAuth:
    return SpotifyOAuth(
        client_id=Config.SPOTIFY_CLIENT_ID,
        client_secret=Config.SPOTIFY_CLIENT_SECRET,
        redirect_uri=Config.SPOTIFY_REDIRECT_URI,
        scope=Config.SPOTIFY_SCOPES,
        cache_handler=MemoryCacheHandler(),
    )


def get_user_token() -> str | None:
    """Return a valid access token if one is stored, refreshing if needed."""
    global _server_token_info
    if not _server_token_info:
        return None
    auth_manager = _get_auth_manager()
    if auth_manager.is_token_expired(_server_token_info):
        _server_token_info = auth_manager.refresh_access_token(
            _server_token_info["refresh_token"]
        )
    return _server_token_info.get("access_token")


@router.get("/auth/login")
async def auth_login():
    """Return the Spotify authorization URL."""
    auth_manager = _get_auth_manager()
    auth_url = auth_manager.get_authorize_url()
    logger.info("Generated Spotify auth URL")
    return {"auth_url": auth_url}


async def handle_auth_callback(code: str):
    """Exchange the authorization code for tokens, store user info, redirect home."""
    global _server_token_info, _authenticated_user
    auth_manager = _get_auth_manager()
    _server_token_info = auth_manager.get_access_token(code, as_dict=True)
    sp = spotipy.Spotify(auth=_server_token_info["access_token"])
    user = sp.current_user()
    _authenticated_user = {
        "display_name": user.get("display_name"),
        "id": user.get("id"),
    }
    logger.info(f"Authenticated as Spotify user: {_authenticated_user['display_name']}")
    return RedirectResponse(url="/")


@router.get("/auth/status")
async def auth_status():
    """Return whether a valid Spotify user token is stored. No external API calls."""
    token = get_user_token()
    if token and _authenticated_user:
        return {
            "authenticated": True,
            "user": _authenticated_user.get("display_name"),
            "user_id": _authenticated_user.get("id"),
        }
    return {"authenticated": False}
