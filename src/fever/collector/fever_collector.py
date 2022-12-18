import requests
import xml.etree.ElementTree as ET
from .collector_base import CollectorBase
from store.store_base import EventsStoreBase

class FeverCollector(CollectorBase):
    
    def __init__(self, store: EventsStoreBase) -> None:
        super().__init__(store)

    def get_data(self):
        xml_data = self.__get_fever_data()
        data = self.__parse_fever_xml_output(xml_data)
        self.events_store.save_events_summary(data)

    @staticmethod
    def __parse_fever_xml_output(content: str) -> list:
        root = ET.fromstring(content)

        flattened_data = []
        for base_event in root.iter('base_event'):
            for event in base_event.iter('event'):
                for zone in event.iter('zone'):
                    flattened_data.append({**base_event.attrib,  **event.attrib, **zone.attrib})
        
        return flattened_data

    @staticmethod
    def __get_fever_data() -> str:

        provider_fever_url = "https://provider.code-challenge.feverup.com/api/events"

        try:
            response = requests.get(provider_fever_url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise RuntimeError(
                f"Error {err} retriving data from provider {provider_fever_url}"
            ) from err

        return response.content
