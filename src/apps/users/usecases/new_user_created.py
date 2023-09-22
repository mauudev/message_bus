from dataclasses import dataclass

from src.core.base_abstractions import Event, Handler
from src.logger import logger


@dataclass(kw_only=True)
class NewUserCreatedEvent(Event):
    id: str
    name: str
    email: str


class NewUserCreated(Handler):
    def handle(self, event: NewUserCreatedEvent):
        logger.info(f"New user created event: {event}")
