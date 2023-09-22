from typing import Any, Callable, Dict, List

from kombu import Connection, Exchange, Queue

from src.core.base_abstractions import Transport
from src.transport.rabbitmq import RabbitMQConsumer, RabbitMQProducer, message_handler


class RabbitMQTransport(Transport):
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
        producer = None
        consumer = None

    def initialize(self) -> None:
        if not self._initialized:
            self._connection = Connection(self._amqp_uri)
            self.producer = RabbitMQProducer(self._connection)
            self.consumer = RabbitMQConsumer(self._connection)

            self._initialized = True

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
                    **self._queue_options,
                )
                queue.declare()
                queues.append(queue)
        return queues

    def publish(self, routing_key: str, message: Any):
        self.producer.push_message(
            message,
            routing_key,
        )

    def consume(self, queue_name: str, callback: Callable[..., Any]) -> None:
        return self..consume(queue_name, callback)
