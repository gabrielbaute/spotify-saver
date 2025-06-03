from spotifysaver.apis.spotify_api import SpotifyAPI

def get_playlist_tracks(playlist_url: str):
    """Obtiene los tracks de una playlist y los imprime."""
    api = SpotifyAPI()
    playlist = api.get_playlist(playlist_url)
    
    print(f"Playlist: {playlist.name} ({playlist.uri})")
    for track in playlist.tracks:
        print(f"{track.number}. {track.name} - {', '.join(track.artists)} - Spotify URI: {track.uri}")

if __name__ == "__main__":
    # Reemplaza con la URL de tu playlist
    playlist_url = "https://open.spotify.com/playlist/01X3ID1BGl5PPky2KFnQ0P"
    get_playlist_tracks(playlist_url)