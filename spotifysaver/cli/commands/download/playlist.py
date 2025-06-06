"""Playlist download command module for SpotifySaver CLI.

This module handles the download process for complete Spotify playlists,
including progress tracking and optional metadata generation.
"""

import click


def process_playlist(spotify, searcher, downloader, url, lyrics, nfo, cover, format, bitrate):
    """Process and download a complete Spotify playlist with progress tracking.
    
    Downloads all tracks from a Spotify playlist, showing a progress bar and
    handling optional features like lyrics and cover art. NFO generation for
    playlists is currently in development.
    
    Args:
        spotify: SpotifyAPI instance for fetching playlist data
        searcher: YoutubeMusicSearcher for finding YouTube matches
        downloader: YouTubeDownloader for downloading and processing files
        url: Spotify playlist URL
        lyrics: Whether to download synchronized lyrics
        nfo: Whether to generate metadata files (in development)
        cover: Whether to download playlist cover art
        format: Audio format for downloaded files
    """
    playlist = spotify.get_playlist(url)
    click.secho(f"\nDownloading playlist: {playlist.name}", fg="magenta")

    # Configure progress bar
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

        # Delegate everything to the downloader
        success, total = downloader.download_playlist_cli(
            playlist,
            download_lyrics=lyrics,
            format=format,
            bitrate=bitrate,
            cover=cover,
            progress_callback=update_progress,
        )

    # Display results
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
    """Generate NFO metadata file for a playlist (similar to albums).
    
    Creates a Jellyfin-compatible NFO file with playlist metadata and optionally
    downloads the playlist cover art. This function is currently in development.
    
    Args:
        downloader: YouTubeDownloader instance for file operations
        playlist: Playlist object with metadata
        cover: Whether to download playlist cover art
    """
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
