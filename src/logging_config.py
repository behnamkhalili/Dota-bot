import logging
import os
import uuid
from logging.handlers import RotatingFileHandler

ROOT_PATH: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(ROOT_PATH, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)


def get_logger() -> logging.Logger:
    logger = logging.getLogger("ETL_Logger")
    if not logger.handlers:
        run_id = uuid.uuid4().hex[:8]
        logger.setLevel(logging.DEBUG)
        file_format = (
            "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s"
        )
        stream_format = "%(asctime)s - %(levelname)s - %(filename)s - %(message)s"

        file_handler = RotatingFileHandler(
            filename=os.path.join(LOGS_DIR, f"ETL-{run_id}.log"),
            mode="a",
            maxBytes=5 * 1024 * 1024,
            backupCount=6,
        )

        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(file_format))

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(logging.Formatter(stream_format))

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
