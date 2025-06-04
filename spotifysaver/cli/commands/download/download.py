"""Download a track, album, or playlist from Spotify via YouTube Music"""

from pathlib import Path

import click

from spotifysaver.services import SpotifyAPI, YoutubeMusicSearcher
from spotifysaver.downloader import YouTubeDownloader
from spotifysaver.spotlog import LoggerConfig
from spotifysaver.cli.commands.download.album import process_album
from spotifysaver.cli.commands.download.playlist import process_playlist
from spotifysaver.cli.commands.download.track import process_track


@click.command("download")
@click.argument("spotify_url")
@click.option("--lyrics", is_flag=True, help="Download synced lyrics (.lrc)")
@click.option("--nfo", is_flag=True, help="Generate Jellyfin NFO file for albums")
@click.option("--cover", is_flag=True, help="Download album cover art")
@click.option("--output", type=Path, default="Music", help="Output directory")
@click.option("--format", type=click.Choice(["m4a", "mp3", "opus"]), default="m4a")
@click.option("--verbose", is_flag=True, help="Show debug output")
def download(
    spotify_url: str,
    lyrics: bool,
    nfo: bool,
    cover: bool,
    output: Path,
    format: str,
    verbose: bool,
):
    """Download a track, album, or playlist from Spotify via YouTube Music"""
    LoggerConfig.setup(level="DEBUG" if verbose else "INFO")

    try:
        spotify = SpotifyAPI()
        searcher = YoutubeMusicSearcher()
        downloader = YouTubeDownloader(base_dir=output)

        if "album" in spotify_url:
            process_album(
                spotify, searcher, downloader, spotify_url, lyrics, nfo, cover, format
            )
        elif "playlist" in spotify_url:
            process_playlist(
                spotify, searcher, downloader, spotify_url, lyrics, nfo, cover, format
            )
        else:
            process_track(spotify, searcher, downloader, spotify_url, lyrics, format)

    except Exception as e:
        click.secho(f"Error: {str(e)}", fg="red", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        raise click.Abort()
