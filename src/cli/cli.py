import click
from pathlib import Path
from src.apis import SpotifyAPI, YoutubeMusicSearcher
from src.downloader import YouTubeDownloader
from src.spotlog import LoggerConfig
from src.config import Config

LoggerConfig.setup()

@click.group()
def cli():
    """Spotify to YouTube Music Downloader"""
    pass

@cli.command()
@click.argument('spotify_url')
@click.option('--lyrics', is_flag=True, help='Download synced lyrics (.lrc)')
@click.option('--output', type=Path, default='Music', help='Output directory')
@click.option('--format', type=click.Choice(['m4a', 'mp3', 'opus']), default='m4a')
@click.option('--verbose', is_flag=True, help='Show debug output')
def download(spotify_url: str, lyrics: bool, output: Path, format: str, verbose: bool):
    """Download a track or album from Spotify via YouTube Music"""
    try:
        spotify = SpotifyAPI()
        searcher = YoutubeMusicSearcher()
        downloader = YouTubeDownloader(base_dir=output)
        
        if verbose:
            click.secho("Modo verbose activado. Se mostrarán mensajes de depuración.", fg='yellow')
            Config.LOG_LEVEL = 'debug'
            LoggerConfig.get_log_level()

        # Detectar si es album o track individual
        if 'album' in spotify_url:
            process_album(spotify, searcher, downloader, spotify_url, lyrics, format)
        else:
            process_track(spotify, searcher, downloader, spotify_url, lyrics, format)
            
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg='red')
        raise click.Abort()

def process_track(spotify, searcher, downloader, url, lyrics, format):
    """Handle single track download"""
    track = spotify.get_track(url)
    yt_url = searcher.search_track(track)
    
    if not yt_url:
        click.secho(f"No se encontró match para: {track.name}", fg='yellow')
        return
    
    audio_path, updated_track = downloader.download_track(track, yt_url, download_lyrics=lyrics)
    
    if audio_path:
        msg = f"Descargado: {track.name}"
        if lyrics and updated_track.has_lyrics:
            msg += " (+ letras)"
        click.secho(msg, fg='green')

def process_album(spotify, searcher, downloader, url, lyrics, format):
    """Handle full album download"""
    album = spotify.get_album(url)
    click.secho(f"\nDescargando álbum: {album.name}", fg='blue')
    
    for i, track in enumerate(album.tracks, 1):
        yt_url = searcher.search_track(track)
        if not yt_url:
            click.secho(f"[{i}/{len(album.tracks)}] No encontrado: {track.name}", fg='yellow')
            continue
        
        audio_path, updated_track = downloader.download_track(track, yt_url, download_lyrics=lyrics)
        status = "✓" if audio_path else "✗"
        color = 'green' if audio_path else 'red'
        
        msg = f"[{i}/{len(album.tracks)}] {status} {track.name}"
        if lyrics and updated_track.has_lyrics:
            msg += " (+ letras)"
        
        click.secho(msg, fg=color)