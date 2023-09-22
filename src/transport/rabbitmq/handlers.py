from typing import Any

from src.logger import logger


def message_handler(message: Any):
    logger.debug(f"Message received on queue handler:{message}")
