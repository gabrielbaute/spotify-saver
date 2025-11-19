import logging
from spotifysaver.metadata.the_audio_db_service import TheAudioDBService

logging.basicConfig(level=logging.INFO)
audiodb = TheAudioDBService()

def get_artist_data(artist: str):
    artist = audiodb.search_artist_by_name(artist)
    return artist

def get_album_data(artist: str, album: str):
    album = audiodb.search_album_by_name(artist, album)
    return album

def get_track_data(artist: str, track: str):
    track = audiodb.search_track_by_name(artist, track)
    return track

def get_tracks_from_album(album_id: str):
    tracks = audiodb.get_tracks_from_an_album(album_id)
    return tracks

if __name__ == "__main__":
    artist = get_artist_data("coldplay")
    album = get_album_data("coldplay", "Parachutes")
    track = get_track_data("coldplay", "yellow")
    album_id = album.get("idAlbum")
    tracks = get_tracks_from_album(album_id)
    for track in tracks:
        print(f"{track.get('intTrackNumber')} - {track.get('strTrack')} - {track.get('strAlbum')} ({int(track.get('intDuration'))/1000}) - Genre: {track.get('strGenre')}")