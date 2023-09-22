from typing import Any, Dict

from kombu import Connection, Exchange, Queue

from src.core.base_abstractions import Transport
from src.logger import logger
from src.transport.rabbitmq import RabbitMQConsumer, RabbitMQProducer, message_handler


class RabbitMQTransport(Transport):
    """
    Initializes a RabbitMQ transport with the provided parameters.

    Args:
        amqp_uri (str): The URI of the RabbitMQ server.
        exchange (str): The name of the exchange to use.
        exchange_type (str): The type of the exchange.
        queues (Dict[str, str]): A dictionary mapping queue names to routing keys.
        queue_options (Dict[str, Any]): A dictionary of additional options for the queues.

    Example:
        ```python
        amqp_uri = "amqp://guest:guest@localhost:5672/"
        exchange = "my_exchange"
        exchange_type = "direct"
        queues = {
            "queue1": "routing_key1",
            "queue2": "routing_key2",
        }
        queue_options = {
            "queue1": {
                "durable": True,
            },
            "queue2": {
                "durable": False,
            },
        }

        transport = RabbitMQTransport(amqp_uri, exchange, exchange_type, queues, queue_options)
        ```"""

    def __init__(
        self,
        amqp_uri: str,
        exchange: str,
        exchange_type: str,
        queues: Dict[str, str],
        queue_options: Dict[str, Any],
    ):
        _amqp_uri = amqp_uri
        _exchange = exchange
        _exchange_type = exchange_type
        _queues = queues
        _queue_options = queue_options
        _initialized = False
        _connection = None
        _declared_queues = None
        producer = None
        consumer = None

    def initialize(self) -> None:
        try:
            if not self._initialized:
                self._connection = Connection(self._amqp_uri)
                self.producer = RabbitMQProducer(self._connection)
                self.consumer = RabbitMQConsumer(self._connection, self.on_message)

                self.declare_exchange(self._exchange, self._exchange_type)
                self._declared_queues = self.declare_queues()

                self._initialized = True
        except Exception as e:
            logger.error(f"Error during transport initialization: {e}")

    def declare_exchange(self, exchange: str, type_: str = "direct"):
        with self._connection.channel() as channel:
            exchange = Exchange(
                name=exchange,
                type=type_,
                channel=channel,
            )
            exchange.declare()
            return exchange

    def declare_queue(
        self, queue_name: str, exchange: str, routing_key: str, options: dict
    ):
        with self._connection.channel() as channel:
            queue = Queue(
                name=queue_name,
                exchange=exchange,
                routing_key=routing_key,
                channel=channel,
                **options,
            )
            queue.declare()
            return queue

    def declare_queues(self):
        queues = []
        with self._connection.channel() as channel:
            for queue_name, routing_key in self._queues.items():
                queue = Queue(
                    name=queue_name,
                    exchange=self._exchange,
                    routing_key=routing_key,
                    channel=channel,
                    **self._queue_options[queue_name]
                    if queue_name in self._queue_options
                    else {},
                )
                queue.declare()
                queues.append(queue)
        return queues

    def publish(self, routing_key: str, message: Any):
        self.producer.push_message(
            message,
            routing_key,
        )

    def on_message(self, body: Any) -> None:
        message_handler(body)
