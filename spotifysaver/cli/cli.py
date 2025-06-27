"""SpotifySaver Command Line Interface Module.

This module provides the main CLI application for SpotifySaver, a tool that downloads
music from Spotify by searching and downloading equivalent tracks from YouTube Music.
The CLI supports downloading individual tracks, albums, and playlists with metadata
preservation and organization features.
"""

from click import group

from spotifysaver.cli.commands import (
    download,
    version,
    inspect,
    show_log,
    init as init_command,
)


@group()
def cli():
    """SpotifySaver - Download music from Spotify via YouTube Music.

    A comprehensive tool for downloading Spotify tracks, albums, and playlists
    by finding equivalent content on YouTube Music. Features include metadata
    preservation, lyrics fetching, and organized file management.
    """
    pass


# Register all available commands
cli.add_command(download)
cli.add_command(inspect)
cli.add_command(version)
cli.add_command(show_log)
cli.add_command(show_log)
cli.add_command(init_command)
