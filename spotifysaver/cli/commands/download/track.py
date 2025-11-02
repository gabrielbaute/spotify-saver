"""Single track download command module for SpotifySaver CLI.

This module handles the download process for individual Spotify tracks,
including YouTube Music search and metadata application.
"""

import click
from spotifysaver.downloader.youtube_downloader import YouTubeDownloader
from spotifysaver.services import SpotifyAPI, YoutubeMusicSearcher, ScoreMatchCalculator

def process_track(
        spotify: SpotifyAPI, 
        searcher: YoutubeMusicSearcher, 
        downloader: YouTubeDownloader, 
        url, 
        lyrics, 
        output_format, 
        bitrate, 
        explain=False
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
    """
    track = spotify.get_track(url)

    if explain:
        scorer = ScoreMatchCalculator()
        click.secho(f"\n🔍 Explaining matches for track: {track.name}", fg="cyan")
        for track in [track]:
            click.secho(f"\n🎵 Track: {track.name}", fg="yellow")
            results = searcher.search_raw(track)
            for result in results:
                explanation = scorer.explain_score(result, track, strict=True)
                click.echo(f"  - Candidate: {explanation['yt_title']}")
                click.echo(f"    Video ID: {explanation['yt_videoId']}")
                click.echo(f"    Duration: {explanation['duration_score']}")
                click.echo(f"    Artist:   {explanation['artist_score']}")
                click.echo(f"    Title:    {explanation['title_score']}")
                click.echo(f"    Album:    {explanation['album_bonus']}")
                click.echo(f"    → Total:  {explanation['total_score']} (passed: {explanation['passed']})")
        return
    
    audio_path, updated_track = downloader.download_track(
        track, 
        output_format=YouTubeDownloader.string_to_audio_format(output_format), 
        bitrate=YouTubeDownloader.int_to_bitrate(bitrate), 
        download_lyrics=lyrics
    )

    if audio_path:
        msg = f"Downloaded: {track.name}"
        if lyrics and updated_track.has_lyrics:
            msg += " (+ lyrics)"
        click.secho(msg, fg="green")
    else:
        click.secho(f"Failed to download: {track.name}", fg="yellow")
