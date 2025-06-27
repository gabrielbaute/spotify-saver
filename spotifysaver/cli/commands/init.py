"""
Init command to configure environment variables for SpotifySaver.
"""

from pathlib import Path
import click


@click.command()
def init():
    """Initialize SpotifySaver configuration by setting up environment variables."""

    # Create the .spotify-saver directory in user's home
    config_dir = Path.home() / ".spotify-saver"
    config_dir.mkdir(exist_ok=True)

    env_file = config_dir / ".env"

    click.echo("🎵 SpotifySaver Configuration Setup")
    click.echo("=" * 40)

    # Prompt for environment variables
    spotify_client_id = click.prompt("Enter your Spotify Client ID", type=str)
    spotify_client_secret = click.prompt(
        "Enter your Spotify Client Secret", type=str, hide_input=True
    )

    # Optional variables with defaults
    download_path = click.prompt(
        "Enter download path",
        default=str(Path.home() / "Downloads" / "SpotifySaver"),
        type=str,
    )

    audio_format = click.prompt(
        "Enter audio format",
        default="mp3",
        type=click.Choice(["mp3", "flac", "ogg", "wav"]),
    )

    audio_quality = click.prompt(
        "Enter audio quality",
        default="320",
        type=click.Choice(["128", "192", "256", "320"]),
    )

    # Write to .env file
    env_content = f"""# SpotifySaver Configuration
SPOTIFY_CLIENT_ID={spotify_client_id}
SPOTIFY_CLIENT_SECRET={spotify_client_secret}
DOWNLOAD_PATH={download_path}
AUDIO_FORMAT={audio_format}
AUDIO_QUALITY={audio_quality}
"""

    with open(env_file, "w", encoding="utf-8") as f:
        f.write(env_content)

    click.echo(f"\n✅ Configuration saved to: {env_file}")
    click.echo("You can now use SpotifySaver commands!")
