from pathlib import Path
import importlib.resources as resources
from http.server import SimpleHTTPRequestHandler


class UIHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for serving the UI files."""

    def __init__(self, *args, **kwargs):
        # Set the directory to serve static files from
        frontend_dir = resources.files("spotifysaver.ui") / "frontend"
        super().__init__(*args, directory=str(frontend_dir), **kwargs)

    def end_headers(self):
        # Add CORS headers
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()
