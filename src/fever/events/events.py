import datetime as dt
from uuid import UUID, uuid4

from typing import List
from enum import Enum
from pydantic import BaseModel, Field

class SellMode(Enum):
    ONLINE = "online"
    OFFline = "offline"


class EventSummary(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    start_date: dt.date
    start_time: dt.time
    end_date: dt.date
    end_time: dt.time
    min_price: float
    max_price: float


class EventList(BaseModel):
    events: List[EventSummary]
