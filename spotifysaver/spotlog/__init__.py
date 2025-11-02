"""Module for logging functionality in Spotify Saver."""

from spotifysaver.spotlog.logger import get_logger
from spotifysaver.spotlog.log_config import LoggerConfig
from spotifysaver.spotlog.ydd_logger import YDLLogger

__all__ = ["get_logger", "LoggerConfig", "YDLLogger"]
