import datetime as dt
import pytz
import json
from uuid import uuid4
import pandas as pd
from events.events import EventList, SellMode, EventSummary
from store.store_base import EventsStoreBase


class DictEventsStore(EventsStoreBase):
    """
    The idea behing this class is to have a easy way to replicate a real DB behavior for testing purposes
    """
    def __init__(self) -> None:
        self.dict_summary_db = []

    def save_events_summary(self, events: list):

        # When saving the data we will already filter the online events to keep only those on the summary store.
        events_df = pd.DataFrame(events)
        events_df = events_df[events_df["sell_mode"] == SellMode.ONLINE.value]
        
        events_df["min_price"] = events_df.groupby("base_event_id")["price"].transform("min")
        events_df["max_price"] = events_df.groupby("base_event_id")["price"].transform("max")

        events_df = events_df[["base_event_id", "title", "event_start_date", "event_end_date", "min_price", "max_price"]]
        events_df = events_df.drop_duplicates()

        events_df["id"] = [str(uuid4()) for _ in range(len(events_df.index))]
        events_df["start_date"] = pd.to_datetime(events_df["event_start_date"]).dt.date
        events_df["start_time"] = pd.to_datetime(events_df["event_start_date"]).dt.time
        events_df["end_date"] = pd.to_datetime(events_df["event_end_date"]).dt.date
        events_df["end_time"] = pd.to_datetime(events_df["event_end_date"]).dt.time

        events_df = events_df.drop(columns=["event_start_date", "event_end_date"]).reset_index(drop=True)

        columns = ["id", "title", "start_date", "start_time", "end_date", "end_time", "min_price", "max_price"]

        if len(self.dict_summary_db) > 0:

            # Check if any existing event has changes, in that case keep the most recent data
            current_data = pd.DataFrame(self.dict_summary_db)[columns]
            changes_df = current_data.merge(events_df[columns], how="inner", left_on="title", right_on="title")

            if len(changes_df.index) > 0:
                current_data = current_data[~current_data["title"].isin(changes_df["title"])]

            self.dict_summary_db = pd.concat([current_data, events_df[columns]]).to_dict("records")

        else:
            self.dict_summary_db = events_df[columns].to_dict("records")

    def get_events_summary(self, starts_at: dt.datetime, ends_at: dt.datetime) -> EventList:
        return [
            event
            for event in self.dict_summary_db
            if (
                (event["start_date"] <= ends_at.date())
                and (event["end_date"] >= starts_at.date())
            )
        ]