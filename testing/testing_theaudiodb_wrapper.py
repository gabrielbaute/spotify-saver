import logging
from spotifysaver.services.the_audio_db_service import TheAudioDBService

logging.basicConfig(level=logging.INFO)
audiodb = TheAudioDBService()

def get_artist_data(artist: str):
    artist = audiodb.get_artist_metadata(artist)
    return artist

def get_album_data(artist: str, album: str):
    album = audiodb.get_album_metadata(artist, album)
    return album

def get_track_data(artist: str, track: str):
    track = audiodb.get_track_metadata(track, artist)
    return track

def get_tracks_from_album(album_id: str):
    tracks = audiodb._get_tracks_from_an_album(album_id)
    return tracks

if __name__ == "__main__":
    artist = get_artist_data("coldplay")
    album = get_album_data("coldplay", "Parachutes")
    track = get_track_data("Queen", "Under Pressure")
    #album_id = album.get("idAlbum")
    #tracks = get_tracks_from_album(album_id)
    #for track in tracks:
    #    print(f"{track.get('intTrackNumber')} - {track.get('strTrack')} - {track.get('strAlbum')} ({int(track.get('intDuration'))/1000}) - Genre: {track.get('strGenre')}")
    #print(f"Tipo: {type(track)}")
    #print("=================")
    #for item in track:
    #    print(f"Item: {item} - Tipo: {type(item)}")
    print(artist.model_dump_json(indent=2))