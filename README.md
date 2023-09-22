# Message Bus

A simple Python library that provides an implementation of a message bus. It allows you to register handlers and dependencies and execute them based on incoming messages simulating communication under CQRS + Event Driven architectures.

## Features

- Register command handlers and event handlers
- Execute handlers based on incoming messages
- Support for persistence to log handled events
- Message sending through amqp with transports

## Installation

Install dependencies via poetry:
```bash
poetry shell
poetry install
```

## Usage

```python from message_bus_library import MessageBus
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
        # others
    },
    "reply": {
        "durable": True,
        # others
    },
}

# Initialization
persistence = InMemoryPersistence()
transport = RabbitMQTransport(amqp_uri, exchange, exchange_type, queues, queue_options)
bus_framework = BusFramework(transport, persistence)
bus_framework.initialize()

# Handler registry
bus_framework.bus.register_command_handler(CreateNewUserCommand, CreateNewUser)
bus_framework.bus.register_event_handler(NewUserCreatedEvent, NewUserCreated)

# Execute
new_user_cmd = CreateNewUserCommand(name="John Doe", email="johndoe@me.com")
response = bus_framework(new_user_cmd)
logger.info(f"Handler response: {response}")
```
