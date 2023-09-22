import os

from src.apps.users.usecases import (
    CreateNewUser,
    CreateNewUserCommand,
    NewUserCreated,
    NewUserCreatedEvent,
)
from src.core.bus import BusFramework
from src.persistence.inmemory_persistence import InMemoryPersistence
from src.transport.rabbitmq_transport import RabbitMQTransport

amqp_uri = os.getenv("AMQP_URI")
exchange = os.getenv("EXCHANGE")
exchange_type = os.getenv("EXCHANGE_TYPE")
queues = {"users": "users_rk", "reply": "reply_rk"}
queue_options = {
    "users": {
        "durable": True,
    },
    "reply": {
        "durable": True,
    },
}

persistence = InMemoryPersistence()
transport = RabbitMQTransport(amqp_uri, exchange, exchange_type, queues, queue_options)
bus_framework = BusFramework(transport, persistence)
bus_framework.initialize()

# Handler registry
bus_framework.bus.register_command_handler(CreateNewUserCommand, CreateNewUser)
bus_framework.bus.register_event_handler(NewUserCreatedEvent, NewUserCreated)
