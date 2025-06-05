"""FastAPI Application Factory"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import download
from .config import APIConfig


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="SpotifySaver API",
        description="Download music from Spotify via YouTube Music with metadata preservation",
        version="0.3.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

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

    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "SpotifySaver API",
            "version": "0.3.0",
            "description": "Download music from Spotify via YouTube Music",
            "docs": "/docs",
            "redoc": "/redoc"
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "SpotifySaver API"}

    return app
