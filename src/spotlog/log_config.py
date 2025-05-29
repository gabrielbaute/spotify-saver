from typing import Optional
from src.config import Config
import logging
import os

class LoggerConfig:
    """Clase para configurar el sistema de logging"""

    LOG_DIR = "logs"
    LOG_FILE = os.path.join(LOG_DIR, "app.log")

    @classmethod
    def _get_log_level(cls) -> int:
        """Obtiene el nivel de logging de las variables de entorno."""
        level_map = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        level_str = Config.LOG_LEVEL
        return level_map.get(level_str, logging.INFO)
    
    @classmethod
    def setup(cls):
        """Inicializa el sistema de logging"""
        os.makedirs(cls.LOG_DIR, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[
                logging.FileHandler(cls.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        logging.info("Logging configurado correctamente.")


# Ejecutar configuración al importar el módulo
LoggerConfig.setup()