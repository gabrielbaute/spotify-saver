"""SpotifySaver CLI - Download Playlist Command"""

import click


def process_playlist(spotify, searcher, downloader, url, lyrics, nfo, cover, format):
    playlist = spotify.get_playlist(url)
    click.secho(f"\nDownloading playlist: {playlist.name}", fg="magenta")

    # Configurar la barra de progreso
    with click.progressbar(
        length=len(playlist.tracks),
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

        # Delegar TODO al downloader
        success, total = downloader.download_playlist_cli(
            playlist,
            download_lyrics=lyrics,
            cover=cover,
            progress_callback=update_progress,
        )

    # Resultados
    if success > 0:
        click.secho(f"\n✔ Downloaded {success}/{total} tracks", fg="green")
        if nfo:
            click.secho(
                f"\nGenerating NFO for playlist: method in development", fg="magenta"
            )
            # generate_nfo_for_playlist(downloader, playlist, cover)
    else:
        click.secho("\n⚠ No tracks downloaded", fg="yellow")


def generate_nfo_for_playlist(downloader, playlist, cover=False):
    """Genera metadata NFO para playlists (similar a álbumes)"""
    try:
        from spotifysaver.metadata import NFOGenerator

        playlist_dir = downloader.base_dir / playlist.name
        NFOGenerator.generate_playlist(playlist, playlist_dir)

        if cover and playlist.cover_url:
            cover_path = playlist_dir / "cover.jpg"
            if not cover_path.exists():
                downloader._save_cover_album(playlist.cover_url, cover_path)
                click.secho(f"✔ Saved playlist cover: {cover_path}", fg="green")

        click.secho(
            f"\n✔ Generated playlist metadata: {playlist_dir}/playlist.nfo", fg="green"
        )
    except Exception as e:
        click.secho(f"\n⚠ Failed to generate NFO: {str(e)}", fg="yellow")
