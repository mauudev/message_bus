# Message Bus

This is a Python library that provides an implementation of a message bus. It allows you to register handlers and dependencies and execute them based on incoming messages. 

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
# Create a MessageBus instance
bus = MessageBus()

# Register command handlers
bus.register_command_handler(MyCommand, MyCommandHandler)

# Register event handlers
bus.register_event_handler(MyEvent, MyEventHandler)

# Execute handlers based on incoming messages
my_command = MyCommand(arg1=1, arg2=2)
bus.handle(my_command)

my_event = MyEvent(arg1="a", arg2="b")
bus.handle(my_event)
```
