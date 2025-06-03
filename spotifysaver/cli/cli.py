import click
from pathlib import Path
from spotifysaver import __version__
from spotifysaver.apis import SpotifyAPI, YoutubeMusicSearcher
from spotifysaver.downloader import YouTubeDownloader
from spotifysaver.spotlog import LoggerConfig
from spotifysaver.config import Config

@click.group()
def cli():
    """Spotify to YouTube Music Downloader"""
    pass

@cli.command('version')
def version():
    """Show current version"""
    click.echo(f"spotifysaver v{__version__}")

@cli.command('download')
@click.argument('spotify_url')
@click.option('--lyrics', is_flag=True, help='Download synced lyrics (.lrc)')
@click.option('--nfo', is_flag=True, help='Generate Jellyfin NFO file for albums')
@click.option('--cover', is_flag=True, help='Download album cover art')
@click.option('--output', type=Path, default='Music', help='Output directory')
@click.option('--format', type=click.Choice(['m4a', 'mp3', 'opus']), default='m4a')
@click.option('--verbose', is_flag=True, help='Show debug output')
def download(spotify_url: str, lyrics: bool, nfo: bool, cover: bool, output: Path, format: str, verbose: bool):
    """Download a track or album from Spotify via YouTube Music"""
    LoggerConfig.setup(level='DEBUG' if verbose else 'INFO')
    
    try:
        spotify = SpotifyAPI()
        searcher = YoutubeMusicSearcher()
        downloader = YouTubeDownloader(base_dir=output)

        # Detectar si es album o track individual
        if 'album' in spotify_url:
            process_album(spotify, searcher, downloader, spotify_url, lyrics, nfo, cover, format)
        else:
            process_track(spotify, searcher, downloader, spotify_url, lyrics, format)
            
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg='red', err=True)
        if verbose:
            click.secho("Traceback:", fg='red', err=True)
            import traceback
            traceback.print_exc()
        raise click.Abort()

def process_track(spotify, searcher, downloader, url, lyrics, format):
    """Handle single track download"""
    track = spotify.get_track(url)
    yt_url = searcher.search_track(track)
    
    if not yt_url:
        click.secho(f"No match found for: {track.name}", fg='yellow')
        return
    
    audio_path, updated_track = downloader.download_track(track, yt_url, download_lyrics=lyrics)
    
    if audio_path:
        msg = f"Downloaded: {track.name}"
        if lyrics and updated_track.has_lyrics:
            msg += " (+ lyrics)"
        click.secho(msg, fg='green')

def process_album(spotify, searcher, downloader, url, lyrics, nfo, format, cover):
    """Handle full album download with optional NFO generation"""
    album = spotify.get_album(url)
    click.secho(f"\nDownloading album: {album.name}", fg='cyan')
    
    results = []
    with click.progressbar(
        album.tracks,
        label='  Downloading tracks',
        fill_char='█',
        empty_char=' ',
        bar_template='  %(label)s  [%(bar)s]  %(info)s',
        show_percent=True,
        show_pos=True,
        width=30,
        color=True,
        item_show_func=lambda t: t.name if t else ''
    ) as bar:
        for track in bar:
            bar.label = f'  Searching: {track.name[:25]}...'
            yt_url = searcher.search_track(track)
            if not yt_url:
                results.append((track, False, "Not found"))
                continue
            
            try:
                bar.label = f"  Downloading {track.name[:25]}..." 
                audio_path, updated_track = downloader.download_track(
                    track, yt_url, download_lyrics=lyrics
                )

                if audio_path:
                    bar.label = f'  Tagging: {track.name[:25]}...'
                
                results.append((track, bool(audio_path), None))
            except Exception as e:
                results.append((track, False, str(e)))

    # Mostrar resumen
    successful = 0
    for i, (track, success, error) in enumerate(results, 1):
        status = "✓" if success else f"✗ ({error})" if error else "✗"
        color = 'green' if success else 'yellow' if error else 'red'
        
        msg = f"[{i}/{len(results)}] {status} {track.name}"
        if success and lyrics and hasattr(track, 'has_lyrics') and track.has_lyrics:
            msg += " (+ lyrics)"
        
        click.secho(msg, fg=color)
        successful += int(success)

    # Generar NFO si se solicita y hay éxitos
    if nfo and successful > 0:
        generate_nfo_for_album(downloader, album, cover)

def generate_nfo_for_album(downloader, album, cover=False):
    """Helper function for NFO generation"""
    try:
        from spotifysaver.metadata.nfo_generator import NFOGenerator
        album_dir = downloader._get_album_dir(album)
        NFOGenerator.generate(album, album_dir)
        
        # Descargar portada si no existe
        if cover and album.cover_url:
            cover_path = album_dir / "cover.jpg"
            if not cover_path.exists() and album.cover_url:
                downloader._save_cover_album(album.cover_url, cover_path)
                click.secho(f"✔ Saved album cover: {album_dir}/cover.jpg", fg='green')
            
        click.secho(f"\n✔ Generated Jellyfin metadata: {album_dir}/album.nfo", fg='green')
    except Exception as e:
        click.secho(f"\n⚠ Failed to generate NFO: {str(e)}", fg='yellow')