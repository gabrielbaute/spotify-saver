"""Track download command module."""

import click


def process_track(spotify, searcher, downloader, url, lyrics, format):
    """Handle single track download"""
    track = spotify.get_track(url)
    yt_url = searcher.search_track(track)

    if not yt_url:
        click.secho(f"No match found for: {track.name}", fg="yellow")
        return

    audio_path, updated_track = downloader.download_track(
        track, yt_url, download_lyrics=lyrics
    )

    if audio_path:
        msg = f"Downloaded: {track.name}"
        if lyrics and updated_track.has_lyrics:
            msg += " (+ lyrics)"
        click.secho(msg, fg="green")
