"""Configuration for SpotifySaver UI Server"""

import os


class UIConfig:
    """Configuration settings for the UI server."""
    
    # Default ports
    DEFAULT_UI_PORT: int = 3000
    DEFAULT_API_PORT: int = 8000
    
    # Server settings
    UI_HOST: str = "localhost"
    API_HOST: str = "0.0.0.0"
    
    # Browser settings
    AUTO_OPEN_BROWSER: bool = True
    
    @classmethod
    def get_ui_port(cls) -> int:
        """Get UI port from environment or default."""
        return int(os.getenv("SPOTIFYSAVER_UI_PORT", str(cls.DEFAULT_UI_PORT)))
    
    @classmethod
    def get_api_port(cls) -> int:
        """Get API port from environment or default."""
        return int(os.getenv("SPOTIFYSAVER_API_PORT", str(cls.DEFAULT_API_PORT)))
    
    @classmethod
    def get_ui_host(cls) -> str:
        """Get UI host from environment or default."""
        return os.getenv("SPOTIFYSAVER_UI_HOST", cls.UI_HOST)
    
    @classmethod
    def get_api_host(cls) -> str:
        """Get API host from environment or default."""
        return os.getenv("SPOTIFYSAVER_API_HOST", cls.API_HOST)
    
    @classmethod
    def should_auto_open_browser(cls) -> bool:
        """Check if browser should be opened automatically."""
        return os.getenv("SPOTIFYSAVER_AUTO_OPEN_BROWSER", "true").lower() == "true"
