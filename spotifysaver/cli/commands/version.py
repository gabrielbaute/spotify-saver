"""Version command module for SpotifySaver CLI.

This module provides the version command that displays the current version
of the SpotifySaver application.
"""

import click

from spotifysaver import __version__


@click.command("version")
def version():
    """Display the current version of SpotifySaver.
    
    Shows the installed version number of the SpotifySaver application.
    This is useful for troubleshooting and ensuring you have the correct version.
    """
    click.echo(f"spotifysaver v{__version__}")
