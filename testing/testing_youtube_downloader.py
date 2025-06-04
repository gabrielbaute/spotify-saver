from spotifysaver.services import SpotifyAPI, YoutubeMusicSearcher
from spotifysaver.downloader import YouTubeDownloader
from spotifysaver.spotlog import get_logger

logger = get_logger("main")

spotify = SpotifyAPI()
searcher = YoutubeMusicSearcher()
downloader = YouTubeDownloader()

album = spotify.get_album("https://open.spotify.com/album/4aoy2NnmDpWvjWi9taOHYe")
for track in album.tracks:
    yt_url = searcher.search_track(track)
    if yt_url:
        downloader.download_track(track, yt_url)