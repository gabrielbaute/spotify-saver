"""Logger for SpotifySaver.
This module provides a function to retrieve a pre-configured logger for the SpotifySaver application.
"""

import logging


def get_logger(name):
    """Devuelve un logger ya configurado"""
    return logging.getLogger(name)
