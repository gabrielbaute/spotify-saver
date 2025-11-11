"""Album download command module for SpotifySaver CLI.

This module handles the download process for complete Spotify albums,
including progress tracking, metadata generation, and cover art download.
"""

import click
from spotifysaver.downloader import YouTubeDownloader, YouTubeDownloaderForCLI
from spotifysaver.services import SpotifyAPI, YoutubeMusicSearcher, ScoreMatchCalculator


def process_album(
        spotify: SpotifyAPI, 
        searcher: YoutubeMusicSearcher, 
        downloader: YouTubeDownloaderForCLI, 
        url, 
        lyrics, 
        nfo, 
        cover, 
        output_format, 
        bitrate, 
        explain=False,
        dry_run=False
        ):
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
        bitrate: Audio bitrate in kbps (96, 128, 192, 256)
        explain: Whether to show score breakdown for each track without downloading
    """
    album = spotify.get_album(url)
    click.secho(f"\nDownloading album: {album.name}", fg="cyan")

    # Explain mode: show score breakdown without downloading
    if explain:
        scorer = ScoreMatchCalculator()
        click.secho(f"\n🔍 Explaining matches for album: {album.name}", fg="cyan")

        for track in album.tracks:
            click.secho(f"\n🎵 Track: {track.name}", fg="yellow")
            results = searcher.search_raw(track)
            
            if not results:
                click.echo("  ⚠ No candidates found.")
                continue
            
            for result in results:
                explanation = scorer.explain_score(result, track, strict=True)
                click.echo(f"  - Candidate: {explanation['yt_title']}")
                click.echo(f"    Video ID: {explanation['yt_videoId']}")
                click.echo(f"    Duration: {explanation['duration_score']}")
                click.echo(f"    Artist:   {explanation['artist_score']}")
                click.echo(f"    Title:    {explanation['title_score']}")
                click.echo(f"    Album:    {explanation['album_bonus']}")
                click.echo(f"    → Total:  {explanation['total_score']} (passed: {explanation['passed']})")
                click.echo("-" * 40)
        
            best = max(results, key=lambda r: scorer.explain_score(r, track)["total_score"])
            best_expl = scorer.explain_score(best, track)
            click.secho(f"\n✅ Best candidate: {best_expl['yt_title']} (score: {best_expl['total_score']})", fg="green")

        return

    # Dry run mode: explain matches without downloading
    if dry_run:
        from spotifysaver.services.score_match_calculator import ScoreMatchCalculator

        scorer = ScoreMatchCalculator()
        click.secho(f"\n🧪 Dry run for album: {album.name}", fg="cyan")

        for track in album.tracks:
            result = searcher.search_track(track)
            explanation = scorer.explain_score(result, track, strict=True)
            click.secho(f"\n🎵 Track: {track.name}", fg="yellow")
            click.echo(f"  → Selected candidate: {explanation['yt_title']}")
            click.echo(f"    Video ID: {explanation['yt_videoId']}")
            click.echo(f"    Total score: {explanation['total_score']} (passed: {explanation['passed']})")
        return


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
