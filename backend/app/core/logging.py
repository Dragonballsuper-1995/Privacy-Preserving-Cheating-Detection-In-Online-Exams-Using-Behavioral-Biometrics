"""
Logging Configuration

Structured logging with rotation and different levels for dev/prod.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json
from datetime import datetime, timezone

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        return json.dumps(log_data)


def setup_logging():
    """
    Configure logging for the application.
    
    - Development: Console output with colored formatting
    - Production: JSON logs to file with rotation
    """
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    
    if settings.environment == "development":
        # Colored console output for development
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
    else:
        # JSON output for production
        console_handler.setFormatter(JSONFormatter())
    
    root_logger.addHandler(console_handler)
    
    # File handlers for production
    if settings.environment == "production":
        # Application log (rotating by size)
        app_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(app_handler)
        
        # Error log (rotating daily)
        error_handler = TimedRotatingFileHandler(
            log_dir / "error.log",
            when="midnight",
            interval=1,
            backupCount=30
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(error_handler)
        
        # Access log for requests
        access_handler = TimedRotatingFileHandler(
            log_dir / "access.log",
            when="midnight",
            interval=1,
            backupCount=7
        )
        access_handler.setLevel(logging.INFO)
        access_handler.setFormatter(JSONFormatter())
        
        access_logger = logging.getLogger("uvicorn.access")
        access_logger.addHandler(access_handler)
    
    # Set levels for third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for {settings.environment} environment")


# Custom logger with context
class ContextLogger:
    """Logger with request context."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context = {}
    
    def set_context(self, **kwargs):
        """Set context for all subsequent log calls."""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear all context."""
        self.context.clear()
    
    def _log(self, level, message, **kwargs):
        """Log with context."""
        extra = {**self.context, **kwargs}
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message, **kwargs):
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message, **kwargs):
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message, **kwargs):
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message, **kwargs):
        self._log(logging.CRITICAL, message, **kwargs)


# Get logger instance
def get_logger(name: str) -> ContextLogger:
    """Get a context logger."""
    return ContextLogger(name)
