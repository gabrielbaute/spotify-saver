"""Module for configuring logging in the Spotify Saver application."""

import logging
import os
from typing import Optional

from spotifysaver.config import Config


class LoggerConfig:
    """Clase para configurar el sistema de logging"""

    LOG_DIR = "logs"
    LOG_FILE = os.path.join(LOG_DIR, "app.log")

    @classmethod
    def get_log_level(cls) -> int:
        """Obtiene el nivel de logging de las variables de entorno."""
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
        """Inicializa el sistema de logging"""
        os.makedirs(cls.LOG_DIR, exist_ok=True)

        log_level = level if level is not None else cls.get_log_level()

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[
                logging.FileHandler(cls.LOG_FILE),
                (
                    logging.StreamHandler()
                    if log_level == logging.DEBUG
                    else logging.NullHandler()
                ),
            ],
        )
        logging.info(f"Logging configured at level: {logging.getLevelName(log_level)}")
