"""Single track download command module for SpotifySaver CLI.

This module handles the download process for individual Spotify tracks,
including YouTube Music search and metadata application.
"""

import click
from spotifysaver.downloader.youtube_downloader import YouTubeDownloader


def process_track(spotify, searcher, downloader, url, lyrics, output_format, bitrate):
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
