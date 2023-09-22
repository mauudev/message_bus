from typing import Any, Callable, Dict, Optional

from .base_abstractions import Message, Persistence, Transport
from .bus import MessageBus
from .exceptions import DependencyAlreadyRegistered


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
        self.error_handlers: Dict[str, Callable] = {}

        self.bus_initialized: bool = False
        self.bus: Optional[MessageBus] = None

    def __call__(self, message: Message) -> Message | None:
        if not self.bus_initialized:
            self._inject_dynamic_dependencies()
            self.bus: MessageBus = MessageBus(
                self.transport, self.persistence, self.error_handlers
            )
            self.bus_initialized = True

        return self.bus.handle(message)

    def add_dependency(self, name, dependency: Any):
        if name in self.dynamic_dep_registry:
            raise DependencyAlreadyRegistered(f"Dependency '{name}' already injected")
        self.dynamic_dep_registry[name] = dependency

    def _inject_dynamic_dependencies(self):
        if "command_handlers_reg" in self._framework_container.message_bus.attributes:
            cmd_handler_registry = self._framework_container.message_bus.attributes[
                "command_handlers_reg"
            ].kwargs

            for _, handler in cmd_handler_registry.items():
                handler.add_attributes(**self.dynamic_dep_registry)

        if "event_handlers_reg" in self._framework_container.message_bus.attributes:
            event_handler_registry = self._framework_container.message_bus.attributes[
                "event_handlers_reg"
            ].kwargs
            for _, handlers in event_handler_registry.items():
                for handler in handlers.args:
                    handler.add_attributes(**self.dynamic_dep_registry)
