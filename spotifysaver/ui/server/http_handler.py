import os
from pathlib import Path
import importlib.resources as resources
from http.server import SimpleHTTPRequestHandler


class UIHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for serving the UI files with SPA support."""

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

    def do_GET(self):
        """Handle GET requests with SPA support."""
        try:
            # Try to serve the requested file normally first
            if self.path == "/" or self.path == "":
                self.path = "/index.html"
            
            # Check if the requested file exists
            requested_file = self.translate_path(self.path)
            
            # If file exists, serve it normally
            if os.path.exists(requested_file) and os.path.isfile(requested_file):
                return super().do_GET()
            
            # If file doesn't exist and it's not an API request, serve index.html for SPA routing
            if not self.path.startswith("/api/"):
                self.path = "/index.html"
                return super().do_GET()
            
            # For API requests that don't exist, return 404
            self.send_error(404, "File not found")
            
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")

    def do_OPTIONS(self):
        """Handle preflight OPTIONS requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
