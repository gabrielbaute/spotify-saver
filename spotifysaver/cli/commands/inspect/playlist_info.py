import click
from spotifysaver.models import Playlist

def show_playlist_info(playlist: Playlist, verbose: bool):
    """Muestra metadata de una playlist."""
    click.secho(f"\n🎧 Playlist: {playlist.name}", fg='green', bold=True)
    click.echo(f"🛠 Creador: {playlist.owner}")
    click.echo(f"📝 Descripción: {playlist.description or 'N/A'}")
    click.echo(f"🎵 Tracks: {len(playlist.tracks)}")
    
    if verbose:
        click.echo(f"\n🔍 Detalles técnicos:")
        click.echo(f"URL de portada: {playlist.cover_url or 'N/A'}")
