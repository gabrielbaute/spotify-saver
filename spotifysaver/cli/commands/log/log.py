"""Log command for displaying the last lines of the log file."""

from pathlib import Path
from typing import Optional

import click

from spotifysaver.spotlog import LoggerConfig  # Importamos la configuración


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
    """Displays the last lines of the log file."""
    log_file = Path(LoggerConfig.get_log_path())

    if path:
        click.echo(f"📁 Log path: {log_file.absolute()}")
        return

    if not log_file.exists():
        click.secho(f"⚠ Log file not found at: {log_file.absolute()}", fg="yellow")
        return

    try:
        with open(log_file, "r", encoding="latin-1") as f:
            all_lines = f.readlines()

        # Filtrar por nivel si se especificó
        filtered_lines = (
            [line for line in all_lines if not level or f"[{level.upper()}]" in line]
            if level
            else all_lines
        )

        # Mostrar las últimas N líneas
        last_n_lines = filtered_lines[-lines:] if lines > 0 else filtered_lines
        click.echo_via_pager("".join(last_n_lines))

    except Exception as e:
        click.secho(f"❌ Error reading the log file: {str(e)}", fg="red")
