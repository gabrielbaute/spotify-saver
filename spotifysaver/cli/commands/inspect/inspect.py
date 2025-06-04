import click
from spotifysaver.spotlog import LoggerConfig
from spotifysaver.services import SpotifyAPI
from spotifysaver.cli.commands.inspect.track_info import show_track_info
from spotifysaver.cli.commands.inspect.album_info import show_album_info
from spotifysaver.cli.commands.inspect.playlist_info import show_playlist_info

@click.command('inspect')
@click.argument('spotify_url')
@click.option('--verbose', is_flag=True, help='Shows technical details')
def inspect(spotify_url: str, verbose: bool):
    """Displays metadata of a track/album/playlist without downloading."""
    LoggerConfig.setup(level='DEBUG' if verbose else 'INFO')
    
    try:
        spotify = SpotifyAPI()
        
        if 'track' in spotify_url:
            obj = spotify.get_track(spotify_url)
            show_track_info(obj, verbose)
        elif 'album' in spotify_url:
            obj = spotify.get_album(spotify_url)
            show_album_info(obj, verbose)
        elif 'playlist' in spotify_url:
            obj = spotify.get_playlist(spotify_url)
            show_playlist_info(obj, verbose)
        else:
            click.secho("⚠ Invalid URL. Must be a track, album, or playlist.", fg='red')
            
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg='red', err=True)
        if verbose:
            import traceback
            traceback.print_exc()