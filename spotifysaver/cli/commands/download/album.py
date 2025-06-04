import click

def process_album(spotify, searcher, downloader, url, lyrics, nfo, cover, format):
    """Maneja la descarga de álbumes mostrando progreso."""
    album = spotify.get_album(url)
    click.secho(f"\nDownloading album: {album.name}", fg="cyan")

    with click.progressbar(
        length=len(album.tracks),
        label="  Processing",
        fill_char="█",
        show_percent=True,
        item_show_func=lambda t: t.name[:25] + "..." if t else "",
    ) as bar:

        def update_progress(idx, total, name):
            bar.label = (
                f"  Downloading: {name[:20]}..."
                if len(name) > 20
                else f"  Downloading: {name}"
            )
            bar.update(1)

        success, total = downloader.download_album_cli(
            album,
            download_lyrics=lyrics,
            nfo=nfo,
            cover=cover,
            progress_callback=update_progress
        )

    # Mostrar resumen
    if success > 0:
        click.secho(f"\n✔ Downloaded {success}/{total} tracks", fg="green")
        if nfo:
            click.secho("✔ Generated album metadata (NFO)", fg="green")
    else:
        click.secho("\n⚠ No tracks downloaded", fg="yellow")

def generate_nfo_for_album(downloader, album, cover=False):
    """Helper function for NFO generation"""
    try:
        from spotifysaver.metadata import NFOGenerator

        album_dir = downloader._get_album_dir(album)
        NFOGenerator.generate(album, album_dir)

        # Descargar portada si no existe
        if cover and album.cover_url:
            cover_path = album_dir / "cover.jpg"
            if not cover_path.exists() and album.cover_url:
                downloader._save_cover_album(album.cover_url, cover_path)
                click.secho(f"✔ Saved album cover: {album_dir}/cover.jpg", fg="green")

        click.secho(
            f"\n✔ Generated Jellyfin metadata: {album_dir}/album.nfo", fg="green"
        )
    except Exception as e:
        click.secho(f"\n⚠ Failed to generate NFO: {str(e)}", fg="yellow")