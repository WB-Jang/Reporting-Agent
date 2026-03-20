"""Application-wide logging configuration."""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger for the given module name.

    Log level is INFO by default.  Set the LOG_LEVEL environment variable
    to override (e.g. DEBUG, WARNING).
    """
    import os

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
