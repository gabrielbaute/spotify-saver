from pathlib import Path
from typing import Optional, NoReturn
from mutagen import File
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TPE2, TALB, TDRC, TRCK, TPOS, TCON
from mutagen.mp4 import MP4, MP4Cover
from mutagen.oggopus import OggOpus

from spotifysaver.models import Track
from spotifysaver.spotlog import get_logger
from spotifysaver.services import TheAudioDBService

class MusicFileMetadata:
    """Handles metadata addition to music files in MP3, M4A, and Opus formats.
    
    Args:
        file_path: Path to the audio file
        track: Track metadata to add
        cover_data: Optional cover art binary data
    """
    def __init__(self, file_path: Path, track: Track, cover_data: Optional[bytes] = None):
        self.file_path = file_path
        self.track = track
        self.cover_data = cover_data
        self.audiodb = TheAudioDBService()
        self.logger = get_logger(f"{self.__class__.__name__}")

    def safe_attr(self, obj, attr):
        """
        Safely get an attribute from an object.
        
        Args:
            obj: Object to get attribute from
            attr: Attribute name
        """
        return getattr(obj, attr, None) if obj else None

    def _get_genre(self, track: Track) -> Optional[str]:
        """Get the genre of a track.
        
        Args:
            track: Track metadata
            
        Returns:
            str: Genre of the track
        """
        self.logger.debug(f"Getting genre for track: {track.number} - {track.name} from TheAudioDB")
        track_data = self.audiodb.get_track_metadata(track.name, track.artists[0])
        self.logger.debug(f"Getting genre for album: {track.album_name} from TheAudioDB")
        album_data = self.audiodb.get_album_metadata(track.album_artist[0], track.album_name)

        track_genre = self.safe_attr(track_data, "genre")
        album_genre = self.safe_attr(album_data, "genre")

        if track_genre:
            self.logger.info(f"Genre found in track: {track_genre}")
            return track_genre
        elif album_genre:
            self.logger.info(f"Genre found in album: {album_genre}")
            return album_genre
        else:
            self.logger.warning("No genre found")
            return None

    def add_metadata(self) -> bool:
        """Add metadata to the audio file.
        
        Returns:
            bool: True if metadata was added successfully
        """
        try:
            if not self.file_path.exists():
                raise FileNotFoundError(f"File {self.file_path} not found")

            handler = {
                '.mp3': self._add_mp3_metadata,
                '.m4a': self._add_m4a_metadata,
                '.opus': self._add_opus_metadata
            }.get(self.file_path.suffix.lower())

            if not handler:
                raise ValueError(f"Unsupported file format: {self.file_path.suffix}")

            handler()
            self.logger.info(f"Metadata added to {self.file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add metadata: {str(e)}")
            return False

    def _add_mp3_metadata(self) -> NoReturn:
        """Add ID3 tags to MP3 files."""
        audio = ID3(str(self.file_path))
        
        
        # Text frames
        frames = [
            TIT2(encoding=3, text=self.track.name), # Title
            TPE1(encoding=3, text="/".join(self.track.artists)), # Artists
            TPE2(encoding=3, text="/".join(self.track.album_artist)), # Album artists
            TALB(encoding=3, text=self.track.album_name), # Album name
            TRCK(encoding=3, text=f"{self.track.number}/{self.track.total_tracks}"), # Track number
            TPOS(encoding=3, text=str(self.track.disc_number)), # Disc number
        ]

        if self.track.release_date:
            frames.append(TDRC(encoding=3, text=self.track.release_date[:4])) # Release year

        genre = self._get_genre(self.track)
        if genre:
            try:
                frames.append(TCON(encoding=3, text=genre)) # Genres
            except:
                self.logger.error(f"Failed to add genre: {genre}")

        # Add all frames
        for frame in frames:
            audio.add(frame)
        
        # Add cover art if available
        if self.cover_data:
            audio.add(APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,  # Front cover
                data=self.cover_data
            ))

        audio.save(v2_version=3)  # ID3v2.3 for maximum compatibility

    def _add_m4a_metadata(self) -> NoReturn:
        """Add metadata to M4A (MP4) files."""
        audio = MP4(str(self.file_path))
        

        audio.update({
            '\xa9nam': [self.track.name],
            '\xa9ART': ["/".join(self.track.artists)],
            'aART': ["/".join(self.track.album_artist)],
            '\xa9alb': [self.track.album_name],
            '\xa9day': [self.track.release_date[:4]],
            'trkn': [(self.track.number, self.track.total_tracks)],
            'disk': [(self.track.disc_number, 1)],
        })

        genre = self._get_genre(self.track)
        if genre:
            audio['\xa9gen'] = [genre]

        if self.cover_data:
            audio['covr'] = [MP4Cover(self.cover_data, imageformat=MP4Cover.FORMAT_JPEG)]

        audio.save()

    def _add_opus_metadata(self) -> NoReturn:
        """Add metadata to Opus files."""
        audio = OggOpus(str(self.file_path))
    
        audio.update({
            'title': self.track.name,
            'artist': "/".join(self.track.artists),
            'album': self.track.album_name,
            'date': self.track.release_date[:4],
            'tracknumber': f"{self.track.number}/{self.track.total_tracks}",
            'discnumber': str(self.track.disc_number),
        })
        
        genre = self._get_genre(self.track)
        if genre:
            audio['genre'] = genre

        if self.cover_data:
            audio['cover'] = self.cover_data

        audio.save()