import datetime as dt

from unittest.mock import MagicMock

from events.events_manager import EventsManager
from store.dict_store import DictEventsStore
from collector.fever_collector import FeverCollector


def test_get_events():

    events_data = [
        {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "title": "string",
            "start_date": "2015-07-20",
            "start_time": "22:38:19",
            "end_date": "2015-07-20",
            "end_time": "14:45:15",
            "min_price": 1.5,
            "max_price": 1.5
        }
    ]
    
    fake_dict_store = DictEventsStore()
    fake_dict_store.get_events_summary = MagicMock(return_value=events_data)

    starts_at = dt.datetime(2022, 1, 1)
    ends_at = dt.datetime(2022, 2, 15)

    events_list = EventsManager(fake_dict_store).get_events_summary(starts_at, ends_at)

    assert len(events_list) > 0


def test_get_events_empty_store():

    events_data = []

    fake_dict_store = DictEventsStore()
    fake_dict_store.get_events = MagicMock(return_value=events_data)

    starts_at = dt.datetime(2022, 1, 1)
    ends_at = dt.datetime(2022, 2, 15)

    events_list = EventsManager(
        fake_dict_store).get_events(starts_at, ends_at)

    assert len(events_list) == 0
