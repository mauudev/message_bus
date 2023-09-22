from threading import Thread
from typing import Any, List, Type

from kombu import Connection, Consumer
from kombu.mixins import ConsumerMixin

from src.logger import logger

from .handlers import message_handler


class RabbitMQConsumer(ConsumerMixin):
    def __init__(self, conn: Connection):
        self.connection = conn
        self._thread = Thread(target=self.run)
        # self.message_handler = message_handler
        self._handler = message_handler

    def get_consumers(self, consumer: Type[Consumer], queues: List[Any]) -> Any:
        return [
            consumer(
                queues=queues,
                callbacks=[self._handler],
                accept=["json"],
                auto_declare=True,
            )
        ]

    def handle_message(self, body, message):
        try:
            self._handler(body)
        except Exception as e:
            logger.error(f"Consumer error processing message: {e}")
        finally:
            message.ack()

    def run_in_thread(self):
        self._thread.start()
        logger.info("Consumer started to run over thread")

    def stop(self):
        self.should_stop = True
        self._thread.join()
        logger.info("Consumer stopped")
