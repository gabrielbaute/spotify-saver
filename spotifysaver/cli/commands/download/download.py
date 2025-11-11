"""Main download command module for SpotifySaver CLI.

This module provides the primary download command that handles downloading
tracks, albums, or playlists from Spotify by finding matching content on
YouTube Music and applying Spotify metadata.
"""

from pathlib import Path

import click

from spotifysaver.services import SpotifyAPI, YoutubeMusicSearcher
from spotifysaver.downloader import YouTubeDownloaderForCLI
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
@click.option("--bitrate", type=int, default=128, help="Audio bitrate in kbps")
@click.option("--verbose", is_flag=True, help="Show debug output")
@click.option("--explain", is_flag=True, help="Show score breakdown for each track without downloading (for error analysis)")
@click.option("--dry-run", is_flag=True, help="Simulate download without saving files")

def download(
    spotify_url: str,
    lyrics: bool,
    nfo: bool,
    cover: bool,
    output: Path,
    format: str,
    bitrate: int,
    verbose: bool,
    explain: bool,
    dry_run: bool,
):
    """Download music from Spotify URLs via YouTube Music with metadata.
    
    This command downloads audio content from YouTube Music that matches
    Spotify tracks, albums, or playlists, then applies the original Spotify
    metadata to create properly organized music files.
    
    Args:
        spotify_url: Spotify URL for track, album, or playlist
        lyrics: Whether to download synchronized lyrics files
        nfo: Whether to generate Jellyfin-compatible metadata files
        cover: Whether to download album/playlist cover art
        output: Base directory for downloaded files
        format: Audio format for downloaded files
        bitrate: Audio bitrate in kbps (96, 128, 192, 256)
        verbose: Whether to show detailed debug information
        explain: Whether to show score breakdown for each track without downloading
    """
    LoggerConfig.setup(level="DEBUG" if verbose else "INFO")

    try:
        spotify = SpotifyAPI()
        searcher = YoutubeMusicSearcher()
        downloader = YouTubeDownloaderForCLI(base_dir=output)

        if "album" in spotify_url:
            process_album(
                spotify, searcher, downloader, spotify_url, lyrics, nfo, cover, format, bitrate, explain, dry_run
            )
        elif "playlist" in spotify_url:
            process_playlist(
                spotify, searcher, downloader, spotify_url, lyrics, nfo, cover, format, bitrate, dry_run
            )
        else:
            process_track(spotify, searcher, downloader, spotify_url, lyrics, format, bitrate, explain, dry_run)

    except Exception as e:
        click.secho(f"Error: {str(e)}", fg="red", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        raise click.Abort()
