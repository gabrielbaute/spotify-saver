"""Example usage scripts for the SpotifySaver API"""

import asyncio
import time
import requests
from typing import Optional

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_V1_URL = f"{API_BASE_URL}/api/v1"


class SpotifySaverAPIClient:
    """Simple client for interacting with the SpotifySaver API."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"

    def inspect_url(self, spotify_url: str) -> dict:
        """Inspect a Spotify URL to get metadata."""
        response = requests.get(
            f"{self.api_url}/inspect", params={"spotify_url": spotify_url}
        )
        response.raise_for_status()
        return response.json()

    def start_download(
        self,
        spotify_url: str,
        download_lyrics: bool = False,
        download_cover: bool = True,
        generate_nfo: bool = False,
        output_format: str = "m4a",
        output_dir: Optional[str] = None,
    ) -> dict:
        """Start a download task."""
        payload = {
            "spotify_url": spotify_url,
            "download_lyrics": download_lyrics,
            "download_cover": download_cover,
            "generate_nfo": generate_nfo,
            "output_format": output_format,
        }
        if output_dir:
            payload["output_dir"] = output_dir

        response = requests.post(f"{self.api_url}/download", json=payload)
        response.raise_for_status()
        return response.json()

    def get_download_status(self, task_id: str) -> dict:
        """Get the status of a download task."""
        response = requests.get(f"{self.api_url}/download/{task_id}/status")
        response.raise_for_status()
        return response.json()

    def cancel_download(self, task_id: str) -> dict:
        """Cancel a download task."""
        response = requests.get(f"{self.api_url}/download/{task_id}/cancel")
        response.raise_for_status()
        return response.json()

    def list_downloads(self) -> dict:
        """List all download tasks."""
        response = requests.get(f"{self.api_url}/downloads")
        response.raise_for_status()
        return response.json()

    def wait_for_completion(self, task_id: str, timeout: int = 600) -> dict:
        """Wait for a download task to complete."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.get_download_status(task_id)

            print(f"Status: {status['status']} - Progress: {status['progress']}%")
            if status.get("current_track"):
                print(f"Current track: {status['current_track']}")

            if status["status"] in ["completed", "failed", "cancelled"]:
                return status

            time.sleep(2)

        raise TimeoutError(f"Download did not complete within {timeout} seconds")


def example_track_download():
    """Example: Download a single track."""
    client = SpotifySaverAPIClient()

    # Spotify track URL (replace with your own)
    spotify_url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"

    print("🎵 SpotifySaver API - Track Download Example")
    print(f"URL: {spotify_url}")

    # First, inspect the track
    print("\n📋 Inspecting track...")
    try:
        metadata = client.inspect_url(spotify_url)
        print(f"Track: {metadata['name']}")
        print(f"Artists: {', '.join(metadata['artists'])}")
        print(f"Album: {metadata.get('album_name', 'N/A')}")
        print(f"Duration: {metadata['duration']}s")
    except Exception as e:
        print(f"Error inspecting track: {e}")
        return

    # Start download
    print("\n⬇️ Starting download...")
    try:
        result = client.start_download(
            spotify_url=spotify_url, download_lyrics=True, download_cover=True
        )
        task_id = result["task_id"]
        print(f"Download started! Task ID: {task_id}")

        # Wait for completion
        final_status = client.wait_for_completion(task_id)

        if final_status["status"] == "completed":
            print(f"\n✅ Download completed!")
            print(f"Output directory: {final_status.get('output_directory')}")
        else:
            print(f"\n❌ Download failed: {final_status.get('error_message')}")

    except Exception as e:
        print(f"Error during download: {e}")


def example_album_download():
    """Example: Download an entire album."""
    client = SpotifySaverAPIClient()

    # Spotify album URL (replace with your own)
    spotify_url = "https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy"

    print("💿 SpotifySaver API - Album Download Example")
    print(f"URL: {spotify_url}")

    # Inspect the album
    print("\n📋 Inspecting album...")
    try:
        metadata = client.inspect_url(spotify_url)
        print(f"Album: {metadata['name']}")
        print(f"Artists: {', '.join(metadata['artists'])}")
        print(f"Release Date: {metadata['release_date']}")
        print(f"Total Tracks: {metadata['total_tracks']}")
    except Exception as e:
        print(f"Error inspecting album: {e}")
        return

    # Start download
    print("\n⬇️ Starting album download...")
    try:
        result = client.start_download(
            spotify_url=spotify_url,
            download_lyrics=True,
            download_cover=True,
            generate_nfo=True,
        )
        task_id = result["task_id"]
        print(f"Download started! Task ID: {task_id}")

        # Wait for completion
        final_status = client.wait_for_completion(task_id, timeout=1800)  # 30 minutes

        if final_status["status"] == "completed":
            print(f"\n✅ Album download completed!")
            print(f"Completed tracks: {final_status['completed_tracks']}")
            print(f"Failed tracks: {final_status['failed_tracks']}")
            print(f"Output directory: {final_status.get('output_directory')}")
        else:
            print(f"\n❌ Download failed: {final_status.get('error_message')}")

    except Exception as e:
        print(f"Error during download: {e}")


def example_playlist_download():
    """Example: Download a playlist."""
    client = SpotifySaverAPIClient()

    # Spotify playlist URL (replace with your own)
    spotify_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"

    print("🎧 SpotifySaver API - Playlist Download Example")
    print(f"URL: {spotify_url}")

    # Inspect the playlist
    print("\n📋 Inspecting playlist...")
    try:
        metadata = client.inspect_url(spotify_url)
        print(f"Playlist: {metadata['name']}")
        print(f"Owner: {metadata['owner']}")
        print(f"Description: {metadata.get('description', 'N/A')}")
        print(f"Total Tracks: {metadata['total_tracks']}")
    except Exception as e:
        print(f"Error inspecting playlist: {e}")
        return

    # Start download
    print("\n⬇️ Starting playlist download...")
    try:
        result = client.start_download(
            spotify_url=spotify_url,
            download_lyrics=False,  # Disable lyrics for faster download
            download_cover=True,
        )
        task_id = result["task_id"]
        print(f"Download started! Task ID: {task_id}")

        # Wait for completion
        final_status = client.wait_for_completion(task_id, timeout=3600)  # 1 hour

        if final_status["status"] == "completed":
            print(f"\n✅ Playlist download completed!")
            print(f"Completed tracks: {final_status['completed_tracks']}")
            print(f"Failed tracks: {final_status['failed_tracks']}")
            print(f"Output directory: {final_status.get('output_directory')}")
        else:
            print(f"\n❌ Download failed: {final_status.get('error_message')}")

    except Exception as e:
        print(f"Error during download: {e}")


if __name__ == "__main__":
    print("SpotifySaver API Examples")
    print("=" * 40)

    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running!")
        else:
            print("❌ API is not responding correctly")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print(
            "Please make sure the API server is running with: python -m spotifysaver.api.main"
        )
        exit(1)

    print("\nChoose an example:")
    print("1. Download a single track")
    print("2. Download an album")
    print("3. Download a playlist")

    choice = input("\nEnter your choice (1-3): ").strip()

    if choice == "1":
        example_track_download()
    elif choice == "2":
        example_album_download()
    elif choice == "3":
        example_playlist_download()
    else:
        print("Invalid choice. Please run the script again.")
