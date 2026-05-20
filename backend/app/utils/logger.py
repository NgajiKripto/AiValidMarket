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


# Convenience functions
def debug(msg, *args, **kwargs):
    get_logger().debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    get_logger().info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    get_logger().warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    get_logger().error(msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    get_logger().critical(msg, *args, **kwargs)
