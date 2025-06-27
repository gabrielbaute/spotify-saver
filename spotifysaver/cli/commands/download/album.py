"""Album download command module for SpotifySaver CLI.

This module handles the download process for complete Spotify albums,
including progress tracking, metadata generation, and cover art download.
"""

import click
from spotifysaver.downloader.youtube_downloader import YouTubeDownloader


def process_album(spotify, searcher, downloader, url, lyrics, nfo, cover, output_format, bitrate):
    """Process and download a complete Spotify album with progress tracking.
    
    Downloads all tracks from a Spotify album, showing a progress bar and
    handling optional features like lyrics, NFO metadata, and cover art.
    
    Args:
        spotify: SpotifyAPI instance for fetching album data
        searcher: YoutubeMusicSearcher for finding YouTube matches
        downloader: YouTubeDownloader for downloading and processing files
        url: Spotify album URL
        lyrics: Whether to download synchronized lyrics
        nfo: Whether to generate Jellyfin metadata files
        cover: Whether to download album cover art
        format: Audio format for downloaded files
    """
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
            output_format=YouTubeDownloader.string_to_audio_format(output_format),
            bitrate=YouTubeDownloader.int_to_bitrate(bitrate),
            nfo=nfo,
            cover=cover,
            progress_callback=update_progress,
        )

    # Display summary
    if success > 0:
        click.secho(f"\n✔ Downloaded {success}/{total} tracks", fg="green")
        if nfo:
            click.secho("✔ Generated album metadata (NFO)", fg="green")
    else:
        click.secho("\n⚠ No tracks downloaded", fg="yellow")


def generate_nfo_for_album(downloader, album, cover=False):
    """Generate NFO metadata file for an album.
    
    Creates a Jellyfin-compatible NFO file with album metadata and optionally
    downloads the album cover art.
    
    Args:
        downloader: YouTubeDownloader instance for file operations
        album: Album object with metadata
        cover: Whether to download album cover art
    """
    try:
        from spotifysaver.metadata import NFOGenerator

        album_dir = downloader._get_album_dir(album)
        NFOGenerator.generate(album, album_dir)

        # Download cover if it doesn't exist
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
