import datetime as dt
from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from events.events_manager import EventsManager
from store.dict_store import DictEventsStore
from collector.fever_collector import FeverCollector
from store.store_base import EventsStoreBase


app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """
    By default Fastapi returns 422 error when there is some issue with the params 
    so we override this error to return the standard 400.
    """
    return JSONResponse(str(exc), status_code=400)

async def get_store():
    # Fill the dict store with the data coming from the provider endpoint.
    # The dict store is used here for simplicity sake but this should be the final storage solution.
    with DictEventsStore() as store:
        FeverCollector(store).get_data()
        yield store


@app.get("/search")
async def search(starts_at: dt.datetime, ends_at: dt.datetime, store: EventsStoreBase = Depends(get_store)):

    events_list = EventsManager(store).get_events_summary(starts_at, ends_at)
    errors = None # TODO: see how to manage errors here

    return {
        "data": {
            "events" :events_list,
        },
        "error": errors
    }
