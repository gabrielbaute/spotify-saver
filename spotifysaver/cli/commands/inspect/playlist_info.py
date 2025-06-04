"""Playlist Information Display Module.

This module provides functionality to display comprehensive playlist information
and metadata from Spotify playlists, including owner details, description,
and track count through the CLI interface.
"""

import click

from spotifysaver.models import Playlist


def show_playlist_info(playlist: Playlist, verbose: bool):
    """Display comprehensive playlist metadata and information.
    
    Shows formatted playlist information including name, creator/owner,
    description, track count, and optionally technical details like
    cover URL when verbose mode is enabled.
    
    Args:
        playlist (Playlist): The playlist object containing metadata to display
        verbose (bool): Whether to show detailed technical information including
                       cover URL and additional metadata
    """
    click.secho(f"\n🎧 Playlist: {playlist.name}", fg="green", bold=True)
    click.echo(f"🛠 Creador: {playlist.owner}")
    click.echo(f"📝 Descripción: {playlist.description or 'N/A'}")
    click.echo(f"🎵 Tracks: {len(playlist.tracks)}")

    if verbose:
        click.echo(f"\n🔍 Detalles técnicos:")
        click.echo(f"URL de portada: {playlist.cover_url or 'N/A'}")
