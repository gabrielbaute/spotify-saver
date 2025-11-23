"""NFO Generator for Jellyfin-compatible XML metadata files.

This module generates XML metadata files (.nfo) that are compatible with Jellyfin
media server for organizing music libraries with proper metadata.
"""

from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
from datetime import datetime
from xml.etree import ElementTree as ET
from xml.dom import minidom

from spotifysaver.models.album import Album
from spotifysaver.services.schemas import AlbumADBResponse
from spotifysaver.services import TheAudioDBService


class NFOGenerator:
    """Generator for Jellyfin-compatible NFO metadata files.
    
    This class provides static methods to generate XML metadata files for albums
    that are compatible with Jellyfin media server. These files contain detailed
    information about albums, tracks, artists, and other metadata.
    """

    @staticmethod
    def _get_theaudiodb_data(album: Album) -> Optional[AlbumADBResponse]:
        service = TheAudioDBService()
        return service.get_album_metadata(album.artists[0], album.name)

    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Convert seconds to MM:SS format.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            str: Formatted duration string in MM:SS format
        """
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

    @staticmethod
    def generate(album: Album, output_dir: Path):
        """Generate an album.nfo file in the specified directory.
        
        Creates a Jellyfin-compatible XML metadata file containing album information,
        track listings, artist details, genres, and other metadata required for
        proper media library organization.

        Args:
            album: Album object containing the album information and tracks
            output_dir: Directory where the album.nfo file will be saved
        """
        # Root element
        root = ET.Element("album")

        # Datos base de Spotify
        ET.SubElement(root, "title").text = album.name
        if album.release_date:
            ET.SubElement(root, "year").text = album.release_date[:4]
            ET.SubElement(root, "premiered").text = album.release_date
            ET.SubElement(root, "releasedate").text = album.release_date

        total_seconds = sum(t.duration for t in album.tracks)
        runtime_minutes = total_seconds // 60
        ET.SubElement(root, "runtime").text = str(runtime_minutes)

        if album.genres:
            for genre in album.genres:
                ET.SubElement(root, "genre").text = genre

        for artist in album.artists:
            ET.SubElement(root, "artist").text = artist
        ET.SubElement(root, "albumartist").text = ", ".join(album.artists)

        # Tracks
        for track in album.tracks:
            track_elem = ET.SubElement(root, "track")
            ET.SubElement(track_elem, "position").text = str(track.number)
            ET.SubElement(track_elem, "title").text = track.name
            ET.SubElement(track_elem, "duration").text = NFOGenerator._format_duration(track.duration)

        # Datos extra de TheAudioDB
        adb_data = NFOGenerator._get_theaudiodb_data(album)
        if adb_data:
            if adb_data.genre:
                ET.SubElement(root, "genre").text = adb_data.genre
            if adb_data.description:
                # description es lista de AlbumDescription → tomar la primera
                desc = adb_data.description[0].description if adb_data.description else ""
                ET.SubElement(root, "review").text = desc
                ET.SubElement(root, "outline").text = desc
            if adb_data.id:
                ET.SubElement(root, "audiodbalbumid").text = str(adb_data.id)
            if adb_data.artist_id:
                ET.SubElement(root, "audiodbartistid").text = str(adb_data.artist_id)
            if adb_data.musicbrainz_id:
                ET.SubElement(root, "musicbrainzalbumid").text = adb_data.musicbrainz_id
            if adb_data.artist_musicbrainz_id:
                ET.SubElement(root, "musicbrainzalbumartistid").text = adb_data.artist_musicbrainz_id

        # Static fields
        ET.SubElement(root, "lockdata").text = "false"
        ET.SubElement(root, "dateadded").text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Pretty XML
        xml_str = ET.tostring(root, encoding="utf-8", method="xml")
        pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")

        nfo_path = output_dir / "album.nfo"
        with open(nfo_path, "w", encoding="utf-8") as f:
            f.write(pretty_xml)
