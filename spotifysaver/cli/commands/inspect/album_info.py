"""Album Information Command Module."""

import click

from spotifysaver.models import Album


def show_album_info(album: Album, verbose: bool):
    """Muestra metadata de un álbum."""
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
