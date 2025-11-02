"""Module for configuring logging in the Spotify Saver application."""

from typing import Optional

import logging
import os

from spotifysaver.config import Config


class LoggerConfig:
    """Configuration class for the application logging system.
    
    This class manages logging configuration including file paths, log levels,
    and handler setup for both file and console output.
    
    Attributes:
        LOG_DIR: Directory where log files are stored
        LOG_FILE: Path to the main application log file
    """

    LOG_DIR = "logs"
    LOG_FILE = os.path.join(LOG_DIR, "app.log")

    @classmethod
    def get_log_path(cls) -> str:
        """Get the absolute path to the log file.
        
        Returns:
            str: Absolute path to the application log file
        """
        return os.path.abspath(cls.LOG_FILE)

    @classmethod
    def get_log_level(cls) -> int:
        """Get the logging level from environment variables.
        
        Returns:
            int: Logging level constant from the logging module
        """
        level_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }
        level_str = Config.LOG_LEVEL
        return level_map.get(level_str, logging.INFO)

    @classmethod
    def setup(cls, level: Optional[int] = None):
        """Initialize the logging system with file and console handlers.
        
        Sets up logging configuration with appropriate formatters and handlers.
        Creates the log directory if it doesn't exist and configures both
        file logging and optional console output for debug mode.
        
        Args:
            level: Optional logging level override. If None, uses environment setting
        """
        os.makedirs(cls.LOG_DIR, exist_ok=True)

        log_level = level if level is not None else cls.get_log_level()

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
            handlers=[
                logging.FileHandler(cls.LOG_FILE, encoding='utf-8'),
                (
                    logging.StreamHandler()
                    if log_level == logging.DEBUG
                    else logging.NullHandler()
                ),
            ],
        )
        logging.info(f"Logging configured at level: {logging.getLevelName(log_level)}")
