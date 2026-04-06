"""Auth command for Spotify user authentication."""

import click
from spotifysaver.services.spotify_api import SpotifyAPI


@click.command("auth", short_help="Authenticate with Spotify for playlist access")
def auth():
    """Authenticate with your Spotify account.

    Opens your browser to authorize SpotifySaver to access your playlists.
    Required for downloading playlists you own or collaborate on.

    Your token is cached at ~/.spotify-saver/.spotify_token_cache.json and
    refreshed automatically on subsequent uses.
    """
    click.echo("Opening browser for Spotify authentication...")
    try:
        spotify = SpotifyAPI()
        user = spotify.sp_user.current_user()
        click.secho(
            f"Authenticated as: {user.get('display_name', user.get('id'))}",
            fg="green",
        )
    except Exception as e:
        click.secho(f"Authentication failed: {e}", fg="red")
        raise SystemExit(1)
