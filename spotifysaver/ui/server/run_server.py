"""UI server entry point for SpotifySaver"""

import os
import sys
import time
import uvicorn
from spotifysaver.api import create_app
from spotifysaver.api.config import APIConfig
from spotifysaver.ui.config import UIConfig
from spotifysaver.ui.server.ui_server import UIServer


def run_ui_server():
    """Entry point for the spotifysaver-ui command."""
    import argparse

    parser = argparse.ArgumentParser(description="SpotifySaver Web Interface")
    parser.add_argument(
        "--ui-port",
        type=int,
        help=f"UI server port (default: {UIConfig.DEFAULT_UI_PORT})",
    )
    parser.add_argument(
        "--api-port",
        type=int,
        help=f"API server port (default: {UIConfig.DEFAULT_API_PORT})",
    )
    parser.add_argument(
        "--ui-host", type=str, help=f"UI server host (default: {UIConfig.UI_HOST})"
    )
    parser.add_argument(
        "--api-host", type=str, help=f"API server host (default: {UIConfig.API_HOST})"
    )
    parser.add_argument(
        "--no-browser", action="store_true", help="Don't open browser automatically"
    )

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
