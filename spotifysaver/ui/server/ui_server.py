import sys
import time
import threading
import subprocess
import webbrowser
from http.server import HTTPServer
from typing import Optional

from spotifysaver.ui.config import UIConfig
from spotifysaver.ui.server.http_handler import UIHandler
from spotifysaver.spotlog import get_logger


class UIServer:
    """Server for SpotifySaver UI that runs both API and frontend."""

    def __init__(self, ui_port: Optional[int] = None, api_port: Optional[int] = None):
        self.logger = get_logger(f"{self.__class__.__name__}")
        self.ui_port = ui_port or UIConfig.get_ui_port()
        self.api_port = api_port or UIConfig.get_api_port()
        self.ui_host = UIConfig.get_ui_host()
        self.api_host = UIConfig.get_api_host()
        self.ui_server: Optional[HTTPServer] = None
        self.api_process: Optional[subprocess.Popen] = None
        self.ui_thread: Optional[threading.Thread] = None

    def start_api_server(self):
        """Start the FastAPI server in a separate process."""
        try:
            self.logger.info(f"Starting API server on port {self.api_port}")

            # Start the API server using uvicorn
            self.api_process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "spotifysaver.api.main:app",
                    "--host",
                    self.api_host,
                    "--port",
                    str(self.api_port),
                    "--reload",
                ]
            )

            # Wait a bit for the server to start
            time.sleep(2)
            self.logger.info("API server started successfully")

        except Exception as e:
            self.logger.error(f"Failed to start API server: {e}")
            raise

    def start_ui_server(self):
        """Start the UI server."""
        try:
            self.logger.info(f"Starting UI server on port {self.ui_port}")

            self.ui_server = HTTPServer((self.ui_host, self.ui_port), UIHandler)
            self.ui_server.serve_forever()

        except Exception as e:
            self.logger.error(f"Failed to start UI server: {e}")
            raise

    def start_ui_thread(self):
        """Start the UI server in a separate thread."""
        self.ui_thread = threading.Thread(target=self.start_ui_server, daemon=True)
        self.ui_thread.start()

    def open_browser(self):
        """Open the web browser to the UI."""
        if not UIConfig.should_auto_open_browser():
            return

        url = f"http://{self.ui_host}:{self.ui_port}"
        try:
            webbrowser.open(url)
            self.logger.info(f"Browser opened to {url}")
        except Exception as e:
            self.logger.warning(f"Could not open browser: {e}")
            self.logger.info(f"Please open your browser manually to: {url}")

    def run(self):
        """Run both servers."""
        try:
            # Start API server
            self.start_api_server()

            # Start UI server in a thread
            self.start_ui_thread()

            # Wait a bit for UI server to start
            time.sleep(1)

            # Open browser
            self.open_browser()

            # Show information
            print("\n" + "=" * 60)
            print("🎵 SpotifySaver UI Server Started!")
            print("=" * 60)
            print(f"📱 Web Interface: http://{self.ui_host}:{self.ui_port}")
            print(f"🔧 API Endpoint:  http://{self.api_host}:{self.api_port}")
            print("=" * 60)
            print("Press Ctrl+C to stop the servers")
            print("=" * 60 + "\n")

            # Keep the main thread alive
            try:
                while True:
                    time.sleep(1)

                    # Check if API process is still running
                    if self.api_process and self.api_process.poll() is not None:
                        self.logger.error("API server stopped unexpectedly")
                        break

            except KeyboardInterrupt:
                self.logger.info("Received shutdown signal")

        except Exception as e:
            self.logger.error(f"Error running servers: {e}")
            raise
        finally:
            self.stop()

    def stop(self):
        """Stop both servers."""
        self.logger.info("Stopping servers...")

        # Stop API server
        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=10)
                self.logger.info("API server stopped")
            except subprocess.TimeoutExpired:
                self.logger.warning("API server did not stop gracefully, killing...")
                self.api_process.kill()
            except Exception as e:
                self.logger.error(f"Error stopping API server: {e}")

        # Stop UI server
        if self.ui_server:
            try:
                self.ui_server.shutdown()
                self.logger.info("UI server stopped")
            except Exception as e:
                self.logger.error(f"Error stopping UI server: {e}")

        self.logger.info("All servers stopped")
