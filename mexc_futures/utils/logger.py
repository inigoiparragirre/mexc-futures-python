"""Logging utilities for MEXC Futures SDK."""

import logging
from datetime import datetime
from enum import IntEnum
from typing import Any, Union


class LogLevel(IntEnum):
    """Log level enumeration."""
    SILENT = 0
    ERROR = 1
    WARN = 2
    INFO = 3
    DEBUG = 4


LogLevelString = Union[str, LogLevel]


class Logger:
    """Logger class with configurable log levels."""
    
    def __init__(self, level: LogLevelString = LogLevel.WARN) -> None:
        """Initialize logger with specified level."""
        if isinstance(level, str):
            level_upper = level.upper()
            self.level = getattr(LogLevel, level_upper, LogLevel.WARN)
        else:
            self.level = level
            
        # Configure Python logger
        self._logger = logging.getLogger('mexc_futures')
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.DEBUG)
    
    def get_level(self) -> LogLevel:
        """Get current log level."""
        return self.level
    
    def is_debug_enabled(self) -> bool:
        """Check if debug logging is enabled."""
        return self.level >= LogLevel.DEBUG
    
    def _log(self, level: LogLevel, *args: Any) -> None:
        """Internal logging method."""
        if self.level >= level:
            message = ' '.join(str(arg) for arg in args)
            
            if level == LogLevel.DEBUG:
                self._logger.debug(message)
            elif level == LogLevel.INFO:
                self._logger.info(message)
            elif level == LogLevel.WARN:
                self._logger.warning(message)
            elif level == LogLevel.ERROR:
                self._logger.error(message)
    
    def debug(self, *args: Any) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, *args)
    
    def info(self, *args: Any) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, *args)
    
    def warn(self, *args: Any) -> None:
        """Log warning message."""
        self._log(LogLevel.WARN, *args)
    
    def error(self, *args: Any) -> None:
        """Log error message."""
        self._log(LogLevel.ERROR, *args)