from typing import Optional, List
from spotifysaver.services.schemas import (
    TrackADBResponse,
    AlbumADBResponse,
    MediaAlbumURLs,
    AlbumDescription,
    MediaArtistURLs,
    ArtistBiography,
    ArtistADBResponse
    )

class AudioDBParser():
    def __init__(self):
        pass

    def parse_track(self, raw_data: dict) -> Optional[TrackADBResponse]:
        """
        Parse track data from TheAudioDB.

        Args:
            raw_data (dict): Raw track data from TheAudioDB.

        Returns:
            TrackADBResponse: Parsed track data.
        """
        if not raw_data:
            return None
        
        track_data = TrackADBResponse(
            id=int(raw_data.get("idTrack", None)),
            name=raw_data.get("strTrack", None),
            album_id=int(raw_data.get("idAlbum", None)),
            album_name=raw_data.get("strAlbum", None),
            artist_id=[int(raw_data.get("idArtist", None))],
            artist_name=[raw_data.get("strArtist", None)],
            duration=int(raw_data.get("intDuration", None)),
            track_number=int(raw_data.get("intTrackNumber", None)),
            genre=raw_data.get("strGenre", None),
            mood=raw_data.get("strMood", None),
            style=raw_data.get("strStyle", None),
            lyrics=raw_data.get("strLyrics", None),
            musicbrainz_id=raw_data.get("strMusicBrainzID", None),
            album_musicbrainz_id=raw_data.get("strMusicBrainzAlbumID", None),
            artist_musicbrainz_id=raw_data.get("strMusicBrainzArtistID", None)
        )
        return track_data
    
    def parse_album_urls(self, raw_data: dict) -> Optional[MediaAlbumURLs]:
        """
        Parse album URLs from TheAudioDB.

        Args:
            raw_data (dict): Raw album data from TheAudioDB.

        Returns:
            MediaAlbumURLs: Parsed album URLs.
        """
        if not raw_data:
            return None

        url_data = MediaAlbumURLs(
            thumb_url=raw_data.get("strAlbumThumb", None),
            back_url=raw_data.get("strAlbumBack", None),
            cd_art_url=raw_data.get("strAlbumCDart", None),
            case_url=raw_data.get("strAlbum3DCase", None),
            face_url=raw_data.get("strAlbumFace", None),
            flat_url=raw_data.get("strAlbum3DFlat", None),
            cd_thumb_url=raw_data.get("strAlbum3DThumb", None)
        )
        return url_data
    
    def parse_album_description(self, raw_data: dict) -> Optional[List[AlbumDescription]]:
        """
        Parse album descriptions from TheAudioDB.

        Args:
            raw_data (dict): Raw album data from TheAudioDB.

        Returns:
            List[AlbumDescription]: Parsed album descriptions.
        """
        if not raw_data:
            return None

        descriptions: List[AlbumDescription] = []
        for key, value in raw_data.items():
            if key.startswith("strDescription"):
                # Extraer el código de idioma (ej. "CN", "IT", "JP", "RU")
                lang_code = key.replace("strDescription", "")
                # Normalizar valor: si viene "None" o None, lo dejamos vacío
                desc_text = None if value in (None, "None") else value
                descriptions.append(
                    AlbumDescription(language=lang_code, description=desc_text or "")
                )

        return descriptions if descriptions else None
    
    def parse_album(self, raw_data: dict) -> AlbumADBResponse:
        """
        Parse album data from TheAudioDB.

        Args:
            raw_data (dict): Raw album data from TheAudioDB.

        Returns:
            AlbumADBResponse: Parsed album data.
        """
        if not raw_data:
            return None
        
        album_data = AlbumADBResponse(
            id=int(raw_data.get("idAlbum", None)),
            name=raw_data.get("strAlbum", None),
            artist_id=int(raw_data.get("idArtist", None)),
            artist_name=raw_data.get("strArtist", None),
            genre=raw_data.get("strGenre", None),
            style=raw_data.get("strStyle", None),
            mood=raw_data.get("strMood", None),
            musicbrainz_id=raw_data.get("strMusicBrainzID"),
            artist_musicbrainz_id=raw_data.get("strMusicBrainzArtistID"),
            release_format=raw_data.get("strReleaseFormat", None),
            release_date=raw_data.get("strReleaseDate", None),
            description=self.parse_album_description(raw_data),
            media_album=self.parse_album_urls(raw_data)
        )
        return album_data

    def parse_artist_urls(self, raw_data: dict) -> MediaArtistURLs:
        """
        Parse artist URLs from TheAudioDB.

        Args:
            raw_data (dict): Raw artist data from TheAudioDB.

        Returns:
            MediaArtistURLs: Parsed artist URLs.
        """
        if not raw_data:
            return None

        url_data = MediaArtistURLs(
            thumb_url=raw_data.get("strArtistThumb", None),
            logo_url=raw_data.get("strArtistLogo", None),
            clearart_url=raw_data.get("strArtistClearart", None),
            wide_thumb_url=raw_data.get("strArtistWideThumb", None),
            banner_url=raw_data.get("strArtistBanner", None),
            fanarts=raw_data.get("strArtistFanart", None)
        )
        return url_data

    def parse_artist_biography(self, raw_data: dict) -> ArtistBiography:
        """
        Parse artist biography from TheAudioDB.

        Args:
            raw_data (dict): Raw artist data from TheAudioDB.

        Returns:
            ArtistBiography: Parsed artist biography.
        """
        if not raw_data:
            return None

        biographies: List[ArtistBiography] = []
        for key, value in raw_data.items():
            if key.startswith("strBiography"):
                #
                lang_code = key.replace("strBiography", "")
                desc_text = None if value in (None, "None") else value
                biographies.append(
                    ArtistBiography(language=lang_code, biography=desc_text or "")
                )
        return biographies if biographies else None

    def parse_artist(self, raw_data: dict) -> ArtistADBResponse:
        """
        Parse artist data from TheAudioDB

        Args:
            raw_data (dict): Raw artist data from TheAudioDB.

        Returns:
            ArtistADBResponse: Parsed artist data.
        """
        if not raw_data:
            return None
        
        artist_data = ArtistADBResponse(
            id=int(raw_data.get("idArtist", None)),
            name=raw_data.get("strArtist", None),
            gender=raw_data.get("strGender", None),
            country=raw_data.get("strCountry", None),
            born_year=int(raw_data.get("intBornYear", None)),
            die_year=int(raw_data.get("intDiedYear", None)),
            style=raw_data.get("strStyle", None),
            genre=raw_data.get("strGenre", None),
            mood=raw_data.get("strMood", None),
            musicbrainz_id=raw_data.get("strMusicBrainzID", None),
            media_artist=self.parse_artist_urls(raw_data),
            biography=self.parse_artist_biography(raw_data)
        )
        return artist_data