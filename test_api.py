#!/usr/bin/env python3
"""
Simple test script for SpotifySaver API
Tests basic API functionality without requiring Spotify credentials.
"""

import requests
import json
import time
from typing import Dict, Any


class SpotifySaverAPIClient:
    """Simple client for SpotifySaver API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def test_basic_endpoints(self) -> Dict[str, Any]:
        """Test basic API endpoints that don't require authentication."""
        results = {}

        # Test root endpoint
        try:
            response = self.session.get(f"{self.base_url}/")
            results["root"] = {
                "status": response.status_code,
                "data": (
                    response.json() if response.status_code == 200 else response.text
                ),
            }
        except Exception as e:
            results["root"] = {"error": str(e)}

        # Test health endpoint
        try:
            response = self.session.get(f"{self.base_url}/health")
            results["health"] = {
                "status": response.status_code,
                "data": (
                    response.json() if response.status_code == 200 else response.text
                ),
            }
        except Exception as e:
            results["health"] = {"error": str(e)}

        # Test downloads list
        try:
            response = self.session.get(f"{self.base_url}/api/v1/downloads")
            results["downloads"] = {
                "status": response.status_code,
                "data": (
                    response.json() if response.status_code == 200 else response.text
                ),
            }
        except Exception as e:
            results["downloads"] = {"error": str(e)}

        return results

    def test_inspect_endpoint(self, spotify_url: str) -> Dict[str, Any]:
        """Test the inspect endpoint (requires Spotify credentials)."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/inspect", params={"spotify_url": spotify_url}
            )
            return {
                "status": response.status_code,
                "data": (
                    response.json() if response.status_code == 200 else response.text
                ),
            }
        except Exception as e:
            return {"error": str(e)}

    def test_download_endpoint(self, spotify_url: str, **kwargs) -> Dict[str, Any]:
        """Test the download endpoint (requires Spotify credentials)."""
        payload = {
            "spotify_url": spotify_url,
            "download_lyrics": kwargs.get("download_lyrics", False),
            "download_cover": kwargs.get("download_cover", True),
            "generate_nfo": kwargs.get("generate_nfo", False),
            "output_format": kwargs.get("output_format", "m4a"),
            "output_dir": kwargs.get("output_dir", None),
        }

        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/download", json=payload
            )
            return {
                "status": response.status_code,
                "data": (
                    response.json() if response.status_code == 200 else response.text
                ),
            }
        except Exception as e:
            return {"error": str(e)}


def main():
    """Main test function."""
    print("🎵 SpotifySaver API Test Script")
    print("=" * 40)

    # Initialize client
    client = SpotifySaverAPIClient()

    # Test basic endpoints
    print("\n1. Testing basic endpoints...")
    basic_results = client.test_basic_endpoints()

    for endpoint, result in basic_results.items():
        status = result.get("status", "ERROR")
        print(f"   {endpoint}: {status}")
        if status == 200:
            print(f"      ✅ Success: {result['data']}")
        else:
            print(f"      ❌ Error: {result.get('data', result.get('error'))}")

    # Test inspect endpoint (will fail without credentials)
    print("\n2. Testing inspect endpoint (without credentials)...")
    inspect_result = client.test_inspect_endpoint(
        "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
    )
    print(f"   Status: {inspect_result.get('status', 'ERROR')}")
    print(f"   Result: {inspect_result.get('data', inspect_result.get('error'))}")

    # Instructions for full testing
    print("\n3. Full API Testing:")
    print("   To test download functionality:")
    print("   1. Set up Spotify API credentials in .env file")
    print("   2. Copy .env.example to .env")
    print("   3. Add your SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET")
    print("   4. Run this script again")

    print("\n✅ Basic API tests completed!")
    print("📚 API Documentation: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
