from abc import ABC
from store.store_base import EventsStoreBase

class CollectorBase(ABC):

    """
    This is the interfaz any external provider should implement. I would probably add here some checks to 
    make sure the data is consistent over the different providers.
    """
    def __init__(
        self,
        store: EventsStoreBase
    ) -> None:
        self.events_store: EventsStoreBase = store

    def get_data(self) -> dict:
        raise NotImplementedError
