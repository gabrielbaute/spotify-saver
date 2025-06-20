"""FastAPI server entry point for SpotifySaver API"""

import uvicorn
from spotifysaver.api import create_app
from spotifysaver.api.config import APIConfig


app = create_app()

def run_server():
    """Run the FastAPI server."""
    uvicorn.run(
        "spotifysaver.api.main:app",
        host=APIConfig.API_HOST,
        port=APIConfig.API_PORT,
        reload=True,
        log_level=APIConfig.LOG_LEVEL,
    )

if __name__ == "__main__":
    run_server()
