from typing import Any

from kombu import Connection, Exchange, Producer, Queue

from src.logger import logger


class RabbitMQProducer:
    def __init__(self, conn: Connection):
        self.connection = conn
        self.exchange = None

    def push_message(
        self,
        message: Any,
        routing_key: str,
    ):
        with self.connection.channel() as channel:
            producer: Producer = Producer(channel)
            try:
                producer.publish(
                    message,
                    exchange=self.exchange,
                    routing_key=routing_key,
                    serializer="json",
                    declare=[self.exchange],
                    retry=True,
                    retry_policy={
                        "interval_start": 0,
                        "interval_step": 2,  # no hardcode
                        "interval_max": 30,
                    },
                )
            except Exception as e:
                logger.error(f"Producer error sending message: {e}")
