from typing import List, Optional
import datetime as dt
from unittest.mock import patch
from store.dict_store import DictEventsStore
from events.events import EventList, EventSummary
from collector.fever_collector import FeverCollector


def flatten_array_dict(data: List) -> List:
    flattened_data = []
    for event in data:
        event = {**event, **event["event"]}
        event.pop("event")
        for zone in event["zones"]:
            flattened_zone = {**event, **zone}
            flattened_zone.pop("zones")
            flattened_data.append(flattened_zone)

    return flattened_data

def get_event_by_title(events: list, title: str) -> Optional[dict]:
    return next((event for event in events if event["title"] == title), None)

@patch.object(FeverCollector, "_FeverCollector__get_fever_data")
@patch.object(FeverCollector, "_FeverCollector__parse_fever_xml_output")
def test_fever_collector_only_online_returned(xml_parse_mock, get_data_mock):
    events_data_1 = [
        {
            "base_event_id": "valid_event_id",
            "sell_mode": "online",
            "title": "Camela en concierto",
            "event": {
                "event_start_date": "2022-01-01T21:00:00",
                "event_end_date": "2022-02-12T22:00:00",
                "event_id": "291",
                "sell_from": "2021-12-01T00:00:00",
                "sell_to": "2021-12-30T20:00:00",
                "sold_out": "false",
                "zones": [
                    {
                        "zone_id": "40",
                        "capacity": "243",
                        "price": "20.00",
                        "name": "Platea",
                        "numbered": "true"
                    },
                    {
                        "zone_id": "38",
                        "capacity": "100",
                        "price": "15.00",
                        "name": "Grada 2",
                        "numbered": "false"
                    }
                ]
            }
        },
        {
            "base_event_id": "invalid_event_id",
            "sell_mode": "offline",
            "title": "Offline event",
            "event": {
                "event_start_date": "2022-01-30T21:00:00",
                "event_end_date": "2022-02-01T22:00:00",
                "event_id": "291",
                "sell_from": "2021-07-01T00:00:00",
                "sell_to": "2021-12-30T20:00:00",
                "sold_out": "false",
                "zones": [
                    {
                        "zone_id": "40",
                        "capacity": "243",
                        "price": "20.00",
                        "name": "Centro",
                        "numbered": "true"
                    }
                ]
            }
        }
    ]

    events_store = DictEventsStore()
    xml_parse_mock.return_value = flatten_array_dict(events_data_1)

    fever_collector = FeverCollector(events_store)
    fever_collector.get_data()

    starts_at = dt.datetime(2022, 1, 1)
    ends_at = dt.datetime(2022, 2, 15)

    result = events_store.get_events_summary(starts_at=starts_at, ends_at=ends_at)
    assert len(result) == 1
    camela_event = get_event_by_title(result, title="Camela en concierto")
    assert camela_event
    assert camela_event["min_price"] == "15.00"
    assert camela_event["max_price"] == "20.00"


@patch.object(FeverCollector, "_FeverCollector__get_fever_data")
@patch.object(FeverCollector, "_FeverCollector__parse_fever_xml_output")
def test_fever_collector_event_updated(xml_parse_mock, get_data_mock):
    events_data_original = [
        {
            "base_event_id": "valid_event_id",
            "sell_mode": "online",
            "title": "Camela en concierto",
            "event": {
                "event_start_date": "2022-01-01T21:00:00",
                "event_end_date": "2022-02-12T22:00:00",
                "event_id": "valid_event_id",
                "sell_from": "2021-12-01T00:00:00",
                "sell_to": "2021-12-30T20:00:00",
                "sold_out": "false",
                "zones": [
                    {
                        "zone_id": "40",
                        "capacity": "243",
                        "price": "20.00",
                        "name": "Platea",
                        "numbered": "true"
                    }
                ]
            }
        }
    ]

    events_data_updated = [
        {
            "base_event_id": "valid_event_id",
            "sell_mode": "online",
            "title": "Camela en concierto",
            "event": {
                "event_start_date": "2022-01-01T21:00:00",
                "event_end_date": "2022-02-12T22:00:00",
                "event_id": "valid_event_id",
                "sell_from": "2021-12-01T00:00:00",
                "sell_to": "2021-12-30T20:00:00",
                "sold_out": "false",
                "zones": [
                    {
                        "zone_id": "40",
                        "capacity": "243",
                        "price": "80.00",  # Price updated
                        "name": "Platea",
                        "numbered": "true"
                    }
                ]
            }
        }
    ]

    events_store = DictEventsStore()
    xml_parse_mock.return_value = flatten_array_dict(events_data_original)

    fever_collector = FeverCollector(events_store)
    fever_collector.get_data()

    xml_parse_mock.return_value = flatten_array_dict(events_data_updated)
    fever_collector.get_data()

    starts_at = dt.datetime(2022, 1, 1)
    ends_at = dt.datetime(2022, 2, 15)

    result = events_store.get_events_summary(starts_at=starts_at, ends_at=ends_at)
    assert len(result) == 1
    camela_event = get_event_by_title(result, title="Camela en concierto")
    assert camela_event
    assert camela_event["min_price"] == "80.00"
    assert camela_event["max_price"] == "80.00"


@patch.object(FeverCollector, "_FeverCollector__get_fever_data")
@patch.object(FeverCollector, "_FeverCollector__parse_fever_xml_output")
def test_fever_collector_event_removed(xml_parse_mock, get_data_mock):
    events_data_original = [
        {
            "base_event_id": "valid_event_id_1",
            "sell_mode": "online",
            "title": "Camela en concierto",
            "event": {
                "event_start_date": "2022-01-01T21:00:00",
                "event_end_date": "2022-02-12T22:00:00",
                "event_id": "valid_event_id_1",
                "sell_from": "2021-12-01T00:00:00",
                "sell_to": "2021-12-30T20:00:00",
                "sold_out": "false",
                "zones": [
                    {
                        "zone_id": "40",
                        "capacity": "243",
                        "price": "20.00",
                        "name": "Platea",
                        "numbered": "true"
                    }
                ]
            }
        },
        {
            "base_event_id": "old_event_id",
            "sell_mode": "online",
            "title": "Event old",
            "event": {
                "event_start_date": "2022-01-01T21:00:00",
                "event_end_date": "2022-02-12T22:00:00",
                "event_id": "old_event_id",
                "sell_from": "2021-12-01T00:00:00",
                "sell_to": "2021-12-30T20:00:00",
                "sold_out": "false",
                "zones": [
                    {
                        "zone_id": "40",
                        "capacity": "243",
                        "price": "20.00",
                        "name": "Platea",
                        "numbered": "true"
                    }
                ]
            }
        }
    ]

    events_data_updated = [{
        "base_event_id": "valid_event_id_3",
        "sell_mode": "online",
        "title": "Evento 3",
        "event": {
            "event_start_date": "2022-01-01T21:00:00",
            "event_end_date": "2022-02-12T22:00:00",
            "event_id": "valid_event_id_3",
            "sell_from": "2021-12-01T00:00:00",
            "sell_to": "2021-12-30T20:00:00",
            "sold_out": "false",
            "zones": [
                {
                        "zone_id": "40",
                        "capacity": "243",
                        "price": "50.00",
                        "name": "Platea",
                        "numbered": "true"
                }
            ]
        }
    }
    ]

    starts_at = dt.datetime(2022, 1, 1)
    ends_at = dt.datetime(2022, 2, 15)

    events_store = DictEventsStore()
    xml_parse_mock.return_value = flatten_array_dict(events_data_original)

    fever_collector = FeverCollector(events_store)
    fever_collector.get_data()

    result = events_store.get_events_summary(starts_at=starts_at, ends_at=ends_at)
    assert len(result) == 2

    xml_parse_mock.return_value = flatten_array_dict(events_data_updated)
    fever_collector.get_data()

    result = events_store.get_events_summary(starts_at=starts_at, ends_at=ends_at)
    assert len(result) == 3


@patch.object(FeverCollector, "_FeverCollector__get_fever_data")
@patch.object(FeverCollector, "_FeverCollector__parse_fever_xml_output")
def test_fever_collector_updated_and_removed_event(xml_parse_mock, get_data_mock):
    events_data_original = [
        {
            "base_event_id": "valid_event_id_1",
            "sell_mode": "online",
            "title": "Camela en concierto",
            "event": {
                "event_start_date": "2022-01-01T21:00:00",
                "event_end_date": "2022-02-12T22:00:00",
                "event_id": "valid_event_id_1",
                "sell_from": "2021-12-01T00:00:00",
                "sell_to": "2021-12-30T20:00:00",
                "sold_out": "false",
                "zones": [
                    {
                        "zone_id": "40",
                        "capacity": "243",
                        "price": "20.00",
                        "name": "Platea",
                        "numbered": "true"
                    }
                ]
            }
        },
        {
            "base_event_id": "old_event_id",
            "sell_mode": "online",
            "title": "Event old",
            "event": {
                "event_start_date": "2022-01-01T21:00:00",
                "event_end_date": "2022-02-12T22:00:00",
                "event_id": "old_event_id",
                "sell_from": "2021-12-01T00:00:00",
                "sell_to": "2021-12-30T20:00:00",
                "sold_out": "false",
                "zones": [
                    {
                        "zone_id": "40",
                        "capacity": "243",
                        "price": "20.00",
                        "name": "Platea",
                        "numbered": "true"
                    }
                ]
            }
        }
    ]

    events_data_updated = [{
        "base_event_id": "valid_event_id_1",
        "sell_mode": "online",
        "title": "Camela en concierto",
        "event": {
            "event_start_date": "2022-01-01T21:00:00",
            "event_end_date": "2022-02-12T22:00:00",
            "event_id": "valid_event_id_3",
            "sell_from": "2021-12-01T00:00:00",
            "sell_to": "2021-12-30T20:00:00",
            "sold_out": "false",
            "zones": [
                {
                        "zone_id": "40",
                        "capacity": "243",
                        "price": "50.00",
                        "name": "Platea",
                        "numbered": "true"
                }
            ]
        }
    }
    ]

    starts_at = dt.datetime(2022, 1, 1)
    ends_at = dt.datetime(2022, 2, 15)

    events_store = DictEventsStore()
    xml_parse_mock.return_value = flatten_array_dict(events_data_original)

    fever_collector = FeverCollector(events_store)
    fever_collector.get_data()

    result = events_store.get_events_summary(starts_at=starts_at, ends_at=ends_at)
    assert len(result) == 2

    xml_parse_mock.return_value = flatten_array_dict(events_data_updated)
    fever_collector.get_data()

    result = events_store.get_events_summary(starts_at=starts_at, ends_at=ends_at)
    assert len(result) == 2
    
    assert get_event_by_title(result, title="Event old")

    camela_event = get_event_by_title(result, title="Camela en concierto")
    assert camela_event
    assert camela_event["min_price"] == "50.00"
    assert camela_event["max_price"] == "50.00"
    