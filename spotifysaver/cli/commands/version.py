"""Version command for spotifysaver CLI."""

import click

from spotifysaver import __version__


@click.command("version")
def version():
    """Show current version"""
    click.echo(f"spotifysaver v{__version__}")
