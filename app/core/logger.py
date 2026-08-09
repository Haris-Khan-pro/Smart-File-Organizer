import logging
from pathlib import Path

from app.core.config import LOG_FILE


def configure_logging() -> logging.Logger:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

    logger = logging.getLogger("smart_file_organizer")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError as error:
        logger.warning(
            "File logging is unavailable at %s; falling back to console logging only. Error: %s",
            LOG_FILE,
            error,
        )

    return logger


logger = configure_logging()
