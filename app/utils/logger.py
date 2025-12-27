import hashlib
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Optional


LOG_FORMAT = "[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(level: str, log_file: Optional[str]) -> None:
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO))
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    root = logging.getLogger()
    root.handlers.clear()

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = TimedRotatingFileHandler(log_file, when="midnight", backupCount=7, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def hash_line_id(line_id: str) -> str:
    return hashlib.sha256(line_id.encode("utf-8")).hexdigest()
