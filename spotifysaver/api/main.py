"""FastAPI server entry point for SpotifySaver API"""

import uvicorn
from spotifysaver.api import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "spotifysaver.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
