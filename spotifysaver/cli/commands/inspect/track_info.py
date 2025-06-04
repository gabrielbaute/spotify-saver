import click
from spotifysaver.models import Track


def show_track_info(track: Track, verbose: bool):
    """Muestra metadata de un track."""
    click.secho(f"\n🎵 Track: {track.name}", fg='cyan', bold=True)
    click.echo(f"👤 Artista(s): {', '.join(track.artists)}")
    click.echo(f"⏱ Duración: {track.duration // 60}:{track.duration % 60:02d}")
    
    if verbose:
        click.echo(f"\n🔍 Detalles técnicos:")
        click.echo(f"URI: {track.uri}")
        click.echo(f"Géneros: {', '.join(track.genres) if track.genres else 'N/A'}")
