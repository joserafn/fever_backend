from typing import List, Optional
import uuid
import datetime as dt

from store.store_base import EventsStoreBase
from events.events import EventList, EventSummary

class EventsManager():
    """
    The purpose of this class is isolate the store from the API.
    """
    def __init__(self, store: EventsStoreBase) -> None:
        self.store: EventsStoreBase = store

    def get_events_summary(self, starts_at: dt.datetime, ends_at: dt.datetime) -> Optional[EventList]:
        return self.store.get_events_summary(starts_at, ends_at)
