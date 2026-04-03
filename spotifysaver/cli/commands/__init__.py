"""
This module provides the command line interface commands for SpotifySaver.
"""

from spotifysaver.cli.commands.download import download
from spotifysaver.cli.commands.version import version
from spotifysaver.cli.commands.inspect import inspect
from spotifysaver.cli.commands.log import show_log
from spotifysaver.cli.commands.init import init
from spotifysaver.cli.commands.auth import auth

__all__ = ["download", "version", "inspect", "show_log", "init", "auth"]
