from uuid import UUID

from src.core.base_abstractions import Event, Persistence


class InMemoryPersistence(Persistence):
    """
    A simple in-memory persistence to keep track of events.
    This shouldn't be used in production because any server restart will always
    erase any registered events.
    """

    def __init__(self):
        self.processed_events = set()

    def save_event(self, event: Event, handler: str):
        event_uuid = event["uuid"]
        self.processed_events.add({"event_uuid": event_uuid, "handler": handler})

    def is_event_processed(self, event_uuid: UUID, handler: str) -> bool:
        for event in self.processed_events:
            return event["event_uuid"] == event_uuid and event["handler"] == handler
        return False
