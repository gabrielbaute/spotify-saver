"""Track Information Display Module.

This module provides functionality to display detailed track information and metadata
from Spotify tracks in a formatted, user-friendly way through the CLI interface.
"""

import click

from spotifysaver.models import Track


def show_track_info(track: Track, verbose: bool):
    """Display comprehensive track metadata and information.
    
    Shows formatted track information including name, artists, duration, and
    optionally technical details like URI and genres when verbose mode is enabled.
    
    Args:
        track (Track): The track object containing metadata to display
        verbose (bool): Whether to show detailed technical information including
                       URI and genres
    """
    click.secho(f"\n🎵 Track: {track.name}", fg="cyan", bold=True)
    click.echo(f"👤 Artista(s): {', '.join(track.artists)}")
    click.echo(f"⏱ Duración: {track.duration // 60}:{track.duration % 60:02d}")

    if verbose:
        click.echo(f"\n🔍 Detalles técnicos:")
        click.echo(f"URI: {track.uri}")
        click.echo(f"Géneros: {', '.join(track.genres) if track.genres else 'N/A'}")
