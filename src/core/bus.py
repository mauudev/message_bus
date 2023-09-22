from typing import Any, Callable, Dict, List, Optional

from src.logger import logger

from .base_abstractions import (
    Bus,
    Command,
    Event,
    Handler,
    Message,
    Persistence,
    Transport,
)
from .exceptions import (
    CommandAlreadyRegistered,
    DependencyAlreadyRegistered,
    InvalidMessageObject,
)


class MessageBus(Bus):
    """
    Implementation of the bus that will register handlers and dependencies.
    The main purpose of this class is to register and execute the handlers based on an incoming message.
    After/before execution, makes use of the persistence object to keep a log of the handled events.
    The relation between commands, events and handlers is:
    :: Command -> CommandHandler
    :: Event -> [EventHandler]
    """

    def __init__(
        self,
        persistence: Persistence,
        transport: Optional[Callable] = None,
        error_handlers: Optional[Dict[str, Callable]] = None,
    ):
        super().__init__()
        self.command_handlers_reg = {}
        self.event_handlers_reg = {}
        self.persistence = persistence
        self.transport = transport
        self.error_handlers: Dict[str, Callable] = error_handlers

    def register_command_handler(self, command: Command, handler: Handler) -> bool:
        logger.info("=> Registering command handler")
        command_name = command.__name__

        if command_name in self.command_handlers_reg:
            raise CommandAlreadyRegistered(
                f"Command '{command_name}' is already registered."
            )

        self.command_handlers_reg[command_name] = handler
        return True

    def register_event_handler(self, event: Event, handler: Handler) -> bool:
        logger.info("=> Registering event handler")
        event_name = event.__name__

        if event_name not in self.event_handlers_reg:
            self.event_handlers_reg[event_name] = [handler]
        elif handler not in self.event_handlers_reg[event_name]:
            self.event_handlers_reg[event_name].append(handler)

        return True

    def handle(self, message: Message) -> Message | None:
        message_name = message.__class__.__name__
        logger.info(f"=> Handling Message: [{message_name}]")
        logger.debug(f"=> Payload: {message}")
        try:
            if isinstance(message, Command):
                if handler := self.command_handlers_reg.get(message_name):
                    return handler(self).handle(message)
            if isinstance(message, Event):
                for handler in self.event_handlers_reg[message_name]:
                    if self.persistence.is_event_processed(
                        message.correlation_id, handler.__name__
                    ):
                        logger.debug(
                            f"Event already processed by: [{handler.__name__}], skipping: [{message}]"
                        )
                        continue
                    handler(self).handle(message)
                    self.persistence.save_event(message, handler.__name__)
            raise InvalidMessageObject(
                f"Unknown message to execute, make sure the message is an Command or Event instance, given: {type(message)}"
            )

        except Exception as error:
            logger.error(f"Error handling message: {error}", exc_info=True)
            if error_handler := self.error_handlers.get(error.__class__.__name__):
                return error_handler(error)
            raise error


class BusFramework:
    """
    Message bus builder, initializes a MessageBus instance and injects dependencies dynamically.
    Here we interact with the Bus at the top layers.
    """

    def __init__(self, transport: Transport, persistence: Persistence):
        self.transport = transport
        self.persistence = persistence

        # Registry for dynamic dependencies injection
        self.dynamic_dep_registry = {}

        # Error handlers
        self.error_handlers: Dict[str, List[Callable]] = {}

        self.bus_initialized: bool = False
        self.bus: Optional[MessageBus] = None

    def __call__(self, message: Message) -> Message | None:
        if not self.bus_initialized:
            self.initialize()
        return self.bus.handle(message)

    def initialize(self):
        if not self.bus_initialized:
            logger.info("=> Initializing bus")
            self.bus: MessageBus = MessageBus(
                self.transport, self.persistence, self.error_handlers
            )
            self._inject_dynamic_dependencies()
            self.bus_initialized = True

    def add_error_handler(self, exc_name: str, handler: Callable):
        if exc_name not in self.error_handlers:
            self.error_handlers[exc_name] = [
                handler,
                *self.error_handlers.get(exc_name, []),
            ]

    def add_handler_dependency(self, name, dependency: Any):
        if name in self.dynamic_dep_registry:
            raise DependencyAlreadyRegistered(f"Dependency '{name}' already injected")
        self.dynamic_dep_registry[name] = dependency

    def _inject_dynamic_dependencies(self):
        for _, handler in self.bus.command_handlers_reg.items():
            handler.add_attributes(**self.dynamic_dep_registry)

        for _, handlers in self.bus.event_handlers_reg.items():
            for handler in handlers:
                handler.add_attributes(**self.dynamic_dep_registry)
