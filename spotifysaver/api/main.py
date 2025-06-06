"""FastAPI server entry point for SpotifySaver API"""

import uvicorn
from spotifysaver.api import create_app

app = create_app()

def run_server():
    """Run the FastAPI server."""
    uvicorn.run(
        "spotifysaver.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

if __name__ == "__main__":
    run_server()
