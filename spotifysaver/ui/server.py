"""UI server entry point for SpotifySaver"""

import os
import sys
import time
import threading
import subprocess
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Optional

import uvicorn
from spotifysaver.api import create_app
from spotifysaver.api.config import APIConfig
from spotifysaver.spotlog import get_logger
from .config import UIConfig

logger = get_logger(__name__)


class UIHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for serving the UI files."""
    
    def __init__(self, *args, **kwargs):
        # Set the directory to serve static files from
        self.directory = str(Path(__file__).parent / "frontend")
        super().__init__(*args, directory=self.directory, **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()


class UIServer:
    """Server for SpotifySaver UI that runs both API and frontend."""
    
    def __init__(self, ui_port: Optional[int] = None, api_port: Optional[int] = None):
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
            logger.info(f"Starting API server on port {self.api_port}")
            
            # Start the API server using uvicorn
            self.api_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn",
                "spotifysaver.api.main:app",
                "--host", self.api_host,
                "--port", str(self.api_port),
                "--reload"
            ])
            
            # Wait a bit for the server to start
            time.sleep(2)
            logger.info("API server started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start API server: {e}")
            raise
    
    def start_ui_server(self):
        """Start the UI server."""
        try:
            logger.info(f"Starting UI server on port {self.ui_port}")
            
            self.ui_server = HTTPServer((self.ui_host, self.ui_port), UIHandler)
            self.ui_server.serve_forever()
            
        except Exception as e:
            logger.error(f"Failed to start UI server: {e}")
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
            logger.info(f"Browser opened to {url}")
        except Exception as e:
            logger.warning(f"Could not open browser: {e}")
            logger.info(f"Please open your browser manually to: {url}")
    
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
            print("\n" + "="*60)
            print("🎵 SpotifySaver UI Server Started!")
            print("="*60)
            print(f"📱 Web Interface: http://{self.ui_host}:{self.ui_port}")
            print(f"🔧 API Endpoint:  http://{self.api_host}:{self.api_port}")
            print("="*60)
            print("Press Ctrl+C to stop the servers")
            print("="*60 + "\n")
            
            # Keep the main thread alive
            try:
                while True:
                    time.sleep(1)
                    
                    # Check if API process is still running
                    if self.api_process and self.api_process.poll() is not None:
                        logger.error("API server stopped unexpectedly")
                        break
                        
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                
        except Exception as e:
            logger.error(f"Error running servers: {e}")
            raise
        finally:
            self.stop()
    
    def stop(self):
        """Stop both servers."""
        logger.info("Stopping servers...")
        
        # Stop API server
        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=10)
                logger.info("API server stopped")
            except subprocess.TimeoutExpired:
                logger.warning("API server did not stop gracefully, killing...")
                self.api_process.kill()
            except Exception as e:
                logger.error(f"Error stopping API server: {e}")
        
        # Stop UI server
        if self.ui_server:
            try:
                self.ui_server.shutdown()
                logger.info("UI server stopped")
            except Exception as e:
                logger.error(f"Error stopping UI server: {e}")
        
        logger.info("All servers stopped")


def run_ui_server():
    """Entry point for the spotifysaver-ui command."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SpotifySaver Web Interface")
    parser.add_argument("--ui-port", type=int, help=f"UI server port (default: {UIConfig.DEFAULT_UI_PORT})")
    parser.add_argument("--api-port", type=int, help=f"API server port (default: {UIConfig.DEFAULT_API_PORT})")
    parser.add_argument("--ui-host", type=str, help=f"UI server host (default: {UIConfig.UI_HOST})")
    parser.add_argument("--api-host", type=str, help=f"API server host (default: {UIConfig.API_HOST})")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    
    args = parser.parse_args()
    
    # Override environment variables with command line arguments
    if args.ui_port:
        os.environ["SPOTIFYSAVER_UI_PORT"] = str(args.ui_port)
    if args.api_port:
        os.environ["SPOTIFYSAVER_API_PORT"] = str(args.api_port)
    if args.ui_host:
        os.environ["SPOTIFYSAVER_UI_HOST"] = args.ui_host
    if args.api_host:
        os.environ["SPOTIFYSAVER_API_HOST"] = args.api_host
    if args.no_browser:
        os.environ["SPOTIFYSAVER_AUTO_OPEN_BROWSER"] = "false"
    
    try:
        server = UIServer()
        server.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_ui_server()
