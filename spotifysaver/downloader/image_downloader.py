import logging
import requests
from pathlib import Path
from typing import Optional
from spotifysaver.config import Config
from spotifysaver.spotlog import get_logger

class ImageDownloader:
    """Downloads images from URLs."""

    def __init__(self):
        """Initialize the ImageDownloader."""
        self.logger = get_logger(f"{self.__class__.__name__}")

    def download_image(self, url: str, output_path: Path) -> Optional[Path]:
        """Download an image from a URL and save it to a specified path.

        Args:
            url: The URL of the image to download.
            output_path: The full path (including filename and extension)
                         where the image should be saved.

        Returns:
            Path: The path to the downloaded image if successful, None otherwise.
        """
        if not url:
            self.logger.warning("No URL provided for image download.")
            return None

        try:
            response = requests.get(url, timeout=Config.DOWNLOAD_TIMEOUT)
            response.raise_for_status()  # Raise an exception for HTTP errors

            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(response.content)
            self.logger.debug(f"Image downloaded successfully to: {output_path}")
            return output_path
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error downloading image from {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while downloading image from {url}: {e}")
            return None
        
    def get_image_from_url(self, url: str) -> Optional[bytes]:
        """Get an image from a URL.
        
        Args:
            url: The URL of the image to download.
            
        Returns:
            bytes: The image data if successful, None otherwise.
        """
        try:
            response = requests.get(url, timeout=Config.DOWNLOAD_TIMEOUT)
            response.raise_for_status()  # Raise an exception for HTTP errors
            self.logger.debug(f"Image downloaded successfully from {url}")
            return response.content if response.status_code == 200 else None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error downloading image from {url}: {e}")
            return None
