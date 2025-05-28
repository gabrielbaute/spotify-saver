# En tu main.py o servicio de descarga
from src.spotify.spotify_api import SpotifyAPI
from src.spotlog.logger import get_logger

logger = get_logger("main")

def download_album(album_url: str):
    api = SpotifyAPI()
    album = api.get_album(album_url)
    
    logger.info(f"Descargando álbum: {album.name} ({', '.join(album.artists)})")
    for track in album.tracks:
        print(f"{album.name} - #{track.number} - {track.name}")

def download_track(track_url: str):
    api = SpotifyAPI()
    track = api.get_track(track_url)
    logger.info(f"Descargando track: {track.name} de {', '.join(track.artists)}")
    print(f"Track Duration: {track.duration} seconds")
    print(f"Track name: {track.name}")
    print(f"Track URI: {track.uri}")
    print(f"Track artists: {', '.join(track.artists)}")
    print(f"Track album: {track.album_name}")

def download_artist(artist_url: str):
    api = SpotifyAPI()
    artist = api.get_artist(artist_url)
    
    logger.info(f"Descargando artista: {artist.name}")
    print(f"Artist Name: {artist.name}")
    print(f"Artist URI: {artist.uri}")
    print(f"Genres: {', '.join(artist.genres)}")
    print(f"Popularity: {artist.popularity}")
    print(f"Followers: {artist.followers}")
    print(f"Image URL: {artist.image_url}")

if __name__ == "__main__":
    print("----\n")
    download_track("https://open.spotify.com/intl-es/track/15NOEMM5HitpLT2QLI5lHC")
    print("----\n")
    download_album("https://open.spotify.com/intl-es/album/4aoy2NnmDpWvjWi9taOHYe")
    print("----\n")
    download_artist("https://open.spotify.com/intl-es/artist/7jxJ25p0pPjk0MStloN6o6")
    print("----\n")