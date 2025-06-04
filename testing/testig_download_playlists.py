from spotifysaver.services import SpotifyAPI, YoutubeMusicSearcher
from spotifysaver.downloader import YouTubeDownloader
from spotifysaver.spotlog import get_logger, LoggerConfig

LoggerConfig.setup()
logger = get_logger("main")

url = "https://open.spotify.com/playlist/01X3ID1BGl5PPky2KFnQ0P"
spotify = SpotifyAPI()
searcher = YoutubeMusicSearcher()
downloader = YouTubeDownloader()

playlist = spotify.get_playlist(url)
for track in playlist.tracks:
    yt_url = searcher.search_track(track)
    if yt_url:
        downloader.download_track(track, yt_url)
    else:
        logger.warning(f"No se encontró YouTube URL para el track: {track.name}")