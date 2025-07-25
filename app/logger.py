import logging
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from pathlib import Path
from queue import Queue


def setup_logging(name: str, log_file: str, level: logging) -> logging.Logger:
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    log_queue = Queue()
    formatter = logging.Formatter(
        "[%(asctime)s]:[%(name)s]:[%(levelname)s] - %(message)s"
    )

    file_handler = RotatingFileHandler(
        filename=log_dir / log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    listener = QueueListener(
        log_queue, file_handler, console_handler, respect_handler_level=True
    )
    listener.start()

    queue_handler = QueueHandler(log_queue)
    logger.addHandler(queue_handler)

    return logger


LOGS = setup_logging("app", "app_logs", logging.DEBUG)
