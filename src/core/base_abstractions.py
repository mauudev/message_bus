from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional
from uuid import UUID, uuid4


@dataclass(kw_only=True)
class Metadata:
    """
    Abstraction that represents a metadata object.
    """

    routing_key: str
    payload: dict


@dataclass(kw_only=True)
class Message:
    """
    Abstraction that represents either a command, event or any object that will
    travel through layers.
    """

    correlation_id: Optional[UUID] = field(default_factory=uuid4)
    version: Optional[int] = field(default=0)
    metadata: Metadata = field(default_factory=dict)


@dataclass(kw_only=True)
class Command(Message):
    """
    Abstraction for all commands in the application to be handled.
    """

    ...


@dataclass(kw_only=True)
class CommandResponse(Message):
    ...


@dataclass(kw_only=True)
class Event(Message):
    """
    Abstraction for all domain events to be handled.
    """

    ...


class Bus(ABC):
    """
    Abstraction for the bus that will register handlers and dependencies.
    """

    @abstractmethod
    def handle(self, dto: Message) -> Message:
        ...


class Handler(ABC):
    """
    Abstraction for the message handler.
    """

    def __init__(self, message_bus: Bus, *args, **kwargs):
        self.message_bus = message_bus

    @abstractmethod
    def handle(self, dto: Message) -> Message:
        ...


class Persistence(ABC):
    """
    Abstraction for the persistence layer.
    """

    @abstractmethod
    def save_event(self, event: Event, handler_name: str):
        ...

    @abstractmethod
    def is_event_processed(self, event_uuid: UUID, handler_name: str) -> bool:
        ...


class Transport(ABC):
    """
    Abstraction for the transport objects.
    """

    @abstractmethod
    def initialize(self) -> None:
        ...

    @abstractmethod
    def declare_queue(
        self, queue_name: str, exchange: str, routing_key: str, options: dict
    ) -> None:
        ...

    @abstractmethod
    def declare_queues(self) -> None:
        ...

    @abstractmethod
    def declare_exchange(self, exchange: str, type_: str) -> None:
        ...

    @abstractmethod
    def publish(self, routing_key: str, message: Any) -> None:
        ...

    @abstractmethod
    def consume(self, queue_name: str, callback: Callable) -> None:
        ...
