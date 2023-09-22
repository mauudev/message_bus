from typing import Any

from src.logger import logger


def message_handler(message_body: Any):
    logger.debug(f"Message received on queue handler:{message_body}")
