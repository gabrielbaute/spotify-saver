"""Single track download command module for SpotifySaver CLI.

This module handles the download process for individual Spotify tracks,
including YouTube Music search and metadata application.
"""

import click
from spotifysaver.downloader import YouTubeDownloaderForCLI, YouTubeDownloader
from spotifysaver.services import SpotifyAPI, YoutubeMusicSearcher, ScoreMatchCalculator

def process_track(
        spotify: SpotifyAPI, 
        searcher: YoutubeMusicSearcher, 
        downloader: YouTubeDownloaderForCLI, 
        url, 
        lyrics, 
        output_format, 
        bitrate, 
        explain=False,
        dry_run=False
        ):
    """Process and download a single Spotify track.
    
    Downloads a single track from Spotify by finding a matching track on
    YouTube Music and applying the original Spotify metadata.
    
    Args:
        spotify: SpotifyAPI instance for fetching track data
        searcher: YoutubeMusicSearcher for finding YouTube matches
        downloader: YouTubeDownloader for downloading and processing files
        url: Spotify track URL
        lyrics: Whether to download synchronized lyrics
        output_format: Audio format for downloaded files
        bitrate: Audio bitrate in kbps (96, 128, 192, 256)
        explain: Whether to show score breakdown without downloading
    """
    track = spotify.get_track(url)

    # Explain mode: show score breakdown without downloading
    if explain:
        scorer = ScoreMatchCalculator()
        click.secho(f"\n🔍 Explaining matches for track: {track.name}", fg="cyan")
        
        click.secho(f"\n🎵 Track: {track.name}", fg="yellow")
        results = searcher.search_raw(track)
        
        if not results:
            click.echo("  ⚠ No candidates found.")
            return
        
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
        scorer = ScoreMatchCalculator()
        click.secho(f"\n🧪 Dry run for track: {track.name}", fg="cyan")
        result = searcher.search_track(track)
        explanation = scorer.explain_score(result, track, strict=True)
        click.echo(f"  → Selected candidate: {explanation['yt_title']}")
        click.echo(f"    Video ID: {explanation['yt_videoId']}")
        click.echo(f"    Total score: {explanation['total_score']} (passed: {explanation['passed']})")
        return

    with click.progressbar(
        length=1,
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

        audio_path, updated_track = downloader.download_track_cli(
            track,
            output_format=YouTubeDownloader.string_to_audio_format(output_format),
            bitrate=YouTubeDownloader.int_to_bitrate(bitrate),
            download_lyrics=lyrics,
            progress_callback=update_progress,
        )


    if audio_path:
        msg = f"Downloaded: {track.name}"
        if lyrics and updated_track.has_lyrics:
            msg += " (+ lyrics)"
        click.secho(msg, fg="green")
    else:
        click.secho(f"Failed to download: {track.name}", fg="yellow")
