"""Logger utility module for SpotifySaver application.

This module provides a simple interface for getting configured loggers
throughout the application.
"""

import logging


def get_logger(name):
    """Get a configured logger instance for the specified module.
    
    Args:
        name: Name of the logger, typically the module name
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
