import click
from pathlib import Path
from spotifysaver import __version__
from spotifysaver.services import SpotifyAPI, YoutubeMusicSearcher
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
    """Download a track, album, or playlist from Spotify via YouTube Music"""
    LoggerConfig.setup(level='DEBUG' if verbose else 'INFO')
    
    try:
        spotify = SpotifyAPI()
        searcher = YoutubeMusicSearcher()
        downloader = YouTubeDownloader(base_dir=output)

        if 'album' in spotify_url:
            process_album(spotify, searcher, downloader, spotify_url, lyrics, nfo, cover, format)
        elif 'playlist' in spotify_url:
            process_playlist(spotify, searcher, downloader, spotify_url, lyrics, nfo, cover, format)
        else:
            process_track(spotify, searcher, downloader, spotify_url, lyrics, format)
            
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg='red', err=True)
        if verbose:
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

def process_album(spotify, searcher, downloader, url, lyrics, nfo, cover, format):
    """Maneja la descarga de álbumes mostrando progreso."""
    album = spotify.get_album(url)
    click.secho(f"\nDownloading album: {album.name}", fg='cyan')

    with click.progressbar(
        length=len(album.tracks),
        label="  Processing",
        fill_char='█',
        show_percent=True,
        item_show_func=lambda t: t.name[:25] + '...' if t else ''
    ) as bar:
        def update_progress(idx, total, name):
            bar.label = f"  Downloading: {name[:20]}..." if len(name) > 20 else f"  Downloading: {name}"
            bar.update(1)

        success, total = downloader.download_album_cli(
            album,
            download_lyrics=lyrics,
            nfo=nfo,
            cover=cover,
            progress_callback=update_progress
        )

    # Mostrar resumen
    if success > 0:
        click.secho(f"\n✔ Downloaded {success}/{total} tracks", fg='green')
        if nfo:
            click.secho("✔ Generated album metadata (NFO)", fg='green')
    else:
        click.secho("\n⚠ No tracks downloaded", fg='yellow')

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

def process_playlist(spotify, searcher, downloader, url, lyrics, nfo, cover, format):
    playlist = spotify.get_playlist(url)
    click.secho(f"\nDownloading playlist: {playlist.name}", fg='magenta')
    
    # Configurar la barra de progreso
    with click.progressbar(
        length=len(playlist.tracks),
        label="  Processing",
        fill_char='█',
        show_percent=True,
        item_show_func=lambda t: t.name[:25] + '...' if t else ''
    ) as bar:
        def update_progress(idx, total, name):
            bar.label = f"  Downloading: {name[:20]}..." if len(name) > 20 else f"  Downloading: {name}"
            bar.update(1)
        
        # Delegar TODO al downloader
        success, total = downloader.download_playlist_cli(
            playlist, 
            download_lyrics=lyrics,
            progress_callback=update_progress
        )

    # Resultados
    if success > 0:
        click.secho(f"\n✔ Downloaded {success}/{total} tracks", fg='green')
        if nfo:
            click.secho(f"\nGenerating NFO for playlist: method in development", fg='magenta')
            #generate_nfo_for_playlist(downloader, playlist, cover)
    else:
        click.secho("\n⚠ No tracks downloaded", fg='yellow')

def generate_nfo_for_playlist(downloader, playlist, cover=False):
    """Genera metadata NFO para playlists (similar a álbumes)"""
    try:
        from spotifysaver.metadata.nfo_generator import NFOGenerator
        playlist_dir = downloader.base_dir / playlist.name
        NFOGenerator.generate_playlist(playlist, playlist_dir)
        
        if cover and playlist.cover_url:
            cover_path = playlist_dir / "cover.jpg"
            if not cover_path.exists():
                downloader._save_cover_album(playlist.cover_url, cover_path)
                click.secho(f"✔ Saved playlist cover: {cover_path}", fg='green')
        
        click.secho(f"\n✔ Generated playlist metadata: {playlist_dir}/playlist.nfo", fg='green')
    except Exception as e:
        click.secho(f"\n⚠ Failed to generate NFO: {str(e)}", fg='yellow')