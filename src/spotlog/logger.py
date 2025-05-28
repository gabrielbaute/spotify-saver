from src.spotlog.log_config import LoggerConfig

LoggerConfig.setup()

import logging

def get_logger(name):
    """Devuelve un logger ya configurado"""
    return logging.getLogger(name)