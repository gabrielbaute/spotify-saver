"""Spotify to YouTube Music Downloader CLI"""

from click import group
from spotifysaver.cli.commands import download, version, inspect, show_log

@group()
def cli():
    """Spotify to YouTube Music Downloader"""
    pass

# Registra todos los comandos
cli.add_command(download)
cli.add_command(inspect)
cli.add_command(version)
cli.add_command(show_log)