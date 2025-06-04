"""Log Display Command Module.

This module provides CLI functionality to display and filter application log files,
allowing users to view recent log entries, filter by log level, and get log file
path information for debugging and monitoring purposes.
"""

from pathlib import Path
from typing import Optional

import click

from spotifysaver.spotlog import LoggerConfig  # Import configuration


@click.command("show-log")
@click.option(
    "--lines", type=int, default=10, help="Number of lines to display (default: 10)"
)
@click.option(
    "--level",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    help="Filter by log level",
)
@click.option(
    "--path",
    is_flag=True,
    help="Show only the path of the log file (no content will be displayed)",
)
def show_log(lines: int, level: Optional[str], path: bool):
    """Display the last lines of the application log file with optional filtering.
    
    This command provides access to application logs with filtering capabilities
    by log level and line count. It can also display just the log file path
    for external log viewing tools.
    
    Args:
        lines (int): Number of recent log lines to display (default: 10)
        level (Optional[str]): Filter logs by specific level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        path (bool): If True, only display the log file path without content
    """
    log_file = Path(LoggerConfig.get_log_path())

    if path:
        click.echo(f"📁 Log path: {log_file.absolute()}")
        return

    if not log_file.exists():
        click.secho(f"⚠ Log file not found at: {log_file.absolute()}", fg="yellow")
        return

    try:
        with open(log_file, "r", encoding="latin-1") as f:
            all_lines = f.readlines()        # Filter by level if specified
        filtered_lines = (
            [line for line in all_lines if not level or f"[{level.upper()}]" in line]
            if level
            else all_lines
        )

        # Display the last N lines
        last_n_lines = filtered_lines[-lines:] if lines > 0 else filtered_lines
        click.echo_via_pager("".join(last_n_lines))

    except Exception as e:
        click.secho(f"❌ Error reading the log file: {str(e)}", fg="red")
