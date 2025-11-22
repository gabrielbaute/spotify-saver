"""FastAPI Application Factory"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .routers import download
from .config import APIConfig
from .. import __version__

def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="SpotifySaver API",
        description="Download music from Spotify via YouTube Music with metadata preservation",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Mount static files
    app.mount("/static", StaticFiles(directory="spotifysaver/ui/static"), name="static")

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=APIConfig.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(download.router, prefix="/api/v1", tags=["download"])

    # Serve the main HTML file
    @app.get("/", tags=["UI"])
    async def read_index():
        """Serve the main index.html file for the UI."""
        return FileResponse('spotifysaver/ui/index.html')

    @app.get("/api/v1/", tags=["Info"])
    async def root():
        """API root endpoint providing basic info.
        name: SpotifySaver API
        version: Current version of the API
        description: Brief description of the API
        """
        return {
            "name": "SpotifySaver API",
            "version": __version__,
            "description": "Download music from Spotify via YouTube Music",
            "docs": "/docs",
            "redoc": "/redoc",
        }

    @app.get("/health", tags=["Info"])
    async def health_check():
        """Health check endpoint to verify API is running."""
        return {"status": "healthy", "service": "SpotifySaver API"}

    @app.get("/version", tags=["Info"])
    async def get_version():
        """Get the current version of the API."""
        return {"version": __version__}

    return app
