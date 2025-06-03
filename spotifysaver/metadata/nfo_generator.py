from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import List
from xml.etree import ElementTree as ET
from xml.dom import minidom
from spotifysaver.models.album import Album

class NFOGenerator:
    """Genera archivos .nfo compatibles con Jellyfin para álbumes musicales."""
    
    @staticmethod
    def generate(album: Album, output_dir: Path):
        """
        Crea un archivo album.nfo en el directorio especificado.
        
        Args:
            album: Objeto Album con la información
            output_dir: Directorio donde se guardará el archivo
        """
        # Elemento raíz
        root = ET.Element("album")
        
        # Metadatos básicos
        ET.SubElement(root, "title").text = album.name
        ET.SubElement(root, "year").text = album.release_date[:4]
        ET.SubElement(root, "premiered").text = album.release_date
        ET.SubElement(root, "releasedate").text = album.release_date
        
        # Duración total (suma de duraciones de tracks en segundos)
        total_seconds = sum(t.duration for t in album.tracks) // 1000
        ET.SubElement(root, "runtime").text = str(total_seconds)
        
        # Géneros (si existen)
        if album.genres:
            for genre in album.genres:
                ET.SubElement(root, "genre").text = genre
        
        # Artistas
        ET.SubElement(root, "artist").text = ", ".join(album.artists)
        ET.SubElement(root, "albumartist").text = ", ".join(album.artists)
        
        # Tracks
        for track in album.tracks:
            track_elem = ET.SubElement(root, "track")
            ET.SubElement(track_elem, "position").text = str(track.number)
            ET.SubElement(track_elem, "title").text = track.name
            ET.SubElement(track_elem, "duration").text = NFOGenerator._format_duration(track.duration)
        
        # Elementos estáticos (opcionales)
        ET.SubElement(root, "review").text = ""
        ET.SubElement(root, "outline").text = ""
        ET.SubElement(root, "lockdata").text = "false"
        ET.SubElement(root, "dateadded").text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Convertir a XML con formato
        xml_str = ET.tostring(root, encoding='utf-8', method='xml')
        pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
        
        # Guardar archivo
        nfo_path = output_dir / "album.nfo"
        with open(nfo_path, "w", encoding="utf-8") as f:
            f.write(pretty_xml)
    
    @staticmethod
    def _format_duration(ms: int) -> str:
        """Convierte milisegundos a formato MM:SS"""
        seconds = (ms // 1000) % 60
        minutes = (ms // (1000 * 60)) % 60
        return f"{minutes:02d}:{seconds:02d}"
