"""NFO Generator for Jellyfin-compatible XML metadata files.

This module generates XML metadata files (.nfo) that are compatible with Jellyfin
media server for organizing music libraries with proper metadata.
"""

from dataclasses import dataclass
from typing import List
from pathlib import Path
from datetime import datetime
from xml.etree import ElementTree as ET
from xml.dom import minidom

from spotifysaver.models.album import Album


class NFOGenerator:
    """Generator for Jellyfin-compatible NFO metadata files.
    
    This class provides static methods to generate XML metadata files for albums
    that are compatible with Jellyfin media server. These files contain detailed
    information about albums, tracks, artists, and other metadata.
    """

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

        # Basic metadata
        ET.SubElement(root, "title").text = album.name
        ET.SubElement(root, "year").text = album.release_date[:4]
        ET.SubElement(root, "premiered").text = album.release_date
        ET.SubElement(root, "releasedate").text = album.release_date

        # Total duration (sum of track durations in seconds)
        total_seconds = sum(t.duration for t in album.tracks) // 1000
        ET.SubElement(root, "runtime").text = str(total_seconds)

        # Genres (if available)
        if album.genres:
            for genre in album.genres:
                ET.SubElement(root, "genre").text = genre

        # Artists
        for artist in album.artists:
            artist_elem = ET.SubElement(root, "artist")
            ET.SubElement(artist_elem, "name").text = artist
        # ET.SubElement(root, "albumartist").text = ", ".join(album.artists)

        # Track listing
        for track in album.tracks:
            track_elem = ET.SubElement(root, "track")
            ET.SubElement(track_elem, "position").text = str(track.number)
            ET.SubElement(track_elem, "title").text = track.name
            ET.SubElement(track_elem, "duration").text = NFOGenerator._format_duration(
                track.duration
            )

        # Static elements (optional Jellyfin fields)
        ET.SubElement(root, "review").text = ""
        ET.SubElement(root, "outline").text = ""
        ET.SubElement(root, "lockdata").text = "false"
        ET.SubElement(root, "dateadded").text = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Convert to formatted XML
        xml_str = ET.tostring(root, encoding="utf-8", method="xml")
        pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")

        # Save file
        nfo_path = output_dir / "album.nfo"
        with open(nfo_path, "w", encoding="utf-8") as f:
            f.write(pretty_xml)

    @staticmethod
    def _format_duration(ms: int) -> str:
        """Convert milliseconds to MM:SS format.
        
        Args:
            ms: Duration in milliseconds
            
        Returns:
            str: Formatted duration string in MM:SS format
        """
        seconds = (ms // 1000) % 60
        minutes = (ms // (1000 * 60)) % 60
        return f"{minutes:02d}:{seconds:02d}"
