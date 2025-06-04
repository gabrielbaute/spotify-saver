"""Album Information Display Module.

This module provides functionality to display comprehensive album information
and metadata from Spotify albums, including tracklist details and technical
information through the CLI interface.
"""

import click

from spotifysaver.models import Album


def show_album_info(album: Album, verbose: bool):
    """Display comprehensive album metadata and tracklist information.
    
    Shows formatted album information including name, artists, release date,
    complete tracklist with durations, and optionally technical details
    like genres when verbose mode is enabled.
    
    Args:
        album (Album): The album object containing metadata and tracks to display
        verbose (bool): Whether to show detailed technical information including
                       genres and additional metadata
    """
    click.secho(f"\n💿 Álbum: {album.name}", fg="magenta", bold=True)
    click.echo(f"👥 Artista(s): {', '.join(album.artists)}")
    click.echo(f"📅 Fecha de lanzamiento: {album.release_date}")
    click.echo(f"🎶 Tracks: {len(album.tracks)}")

    click.echo("Tracklist:")
    for track in album.tracks:
        click.echo(
            f"  - {track.name} ({track.duration // 60}:{track.duration % 60:02d})"
        )

    if verbose:
        click.echo(f"\n🔍 Detalles técnicos:")
        click.echo(f"Géneros: {', '.join(album.genres) if album.genres else 'N/A'}")
