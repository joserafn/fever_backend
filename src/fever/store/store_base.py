from abc import abstractmethod, ABC
from abc import ABC
import datetime as dt
from events.events import EventList


class EventsStoreBase(ABC):
    """
    Interface to define what operations must implement any store child class
    """
    def __enter__(self):
        """
        This method is needed in order to make any child class behave like a context manager 
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        This method is needed in order to make any child class behave like a context manager 
        """
        pass

    @abstractmethod
    def save_events_summary(events:list):
        raise NotImplementedError

    @abstractmethod
    def get_events_summary(self, starts_at: dt.datetime, ends_at: dt.datetime) -> EventList:
        raise NotImplementedError
