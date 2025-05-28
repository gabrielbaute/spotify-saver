import logging
import os

class LoggerConfig:
    """Clase para configurar el sistema de logging"""

    LOG_DIR = "logs"
    LOG_FILE = os.path.join(LOG_DIR, "app.log")

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