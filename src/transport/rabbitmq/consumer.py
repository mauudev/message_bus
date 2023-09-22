from threading import Thread
from typing import Any, Callable, List, Type

from kombu import Connection, Consumer
from kombu.mixins import ConsumerMixin

from src.logger import logger


class RabbitMQConsumer(ConsumerMixin):
    def __init__(self, conn: Connection, message_handler: Callable):
        self.connection = conn
        self._thread = Thread(target=self.run)
        self._message_handler = message_handler

    def get_consumers(self, consumer: Type[Consumer], queues: List[Any]) -> Any:
        return [
            consumer(
                queues=queues,
                callbacks=[self.on_message],
                accept=["json"],
                auto_declare=True,
            )
        ]

    def on_message(self, body, message):
        self._message_handler(body)
        message.ack()

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
