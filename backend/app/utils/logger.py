import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Log directory
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Logger instance
_logger = None


def setup_logger(name="aivalidmarket", level=logging.DEBUG):
    """Set up the application logger with file and console handlers."""
    global _logger

    _logger = logging.getLogger(name)
    _logger.setLevel(level)

    # Avoid duplicate handlers
    if _logger.handlers:
        return _logger

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # File handler with rotation
    file_handler = RotatingFileHandler(
        LOG_DIR / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)

    return _logger


def get_logger():
    """Get the application logger, creating it if necessary."""
    global _logger
    if _logger is None:
        setup_logger()
    return _logger


def _sanitize(msg):
    """Sanitize a log message to prevent log injection."""
    from app.utils.sanitizer import sanitize_log_input
    if isinstance(msg, str):
        return sanitize_log_input(msg, max_length=2000)
    return msg


# Convenience functions
def debug(msg, *args, **kwargs):
    get_logger().debug(_sanitize(msg), *args, **kwargs)


def info(msg, *args, **kwargs):
    get_logger().info(_sanitize(msg), *args, **kwargs)


def warning(msg, *args, **kwargs):
    get_logger().warning(_sanitize(msg), *args, **kwargs)


def error(msg, *args, **kwargs):
    get_logger().error(_sanitize(msg), *args, **kwargs)


def critical(msg, *args, **kwargs):
    get_logger().critical(_sanitize(msg), *args, **kwargs)
