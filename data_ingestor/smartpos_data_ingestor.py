from data_ingestor.data_ingestor import DataIngestorInterface
from typing import Optional
from utils.tools.log_tool import log_message

class SmartPOSDataIngestor(DataIngestorInterface):
    """Singleton class for SmartPOS data ingestion."""
    _instance: Optional[DataIngestorInterface] = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self) -> None:
        # Initialization logic for SmartPOS data ingestion
        pass

    async def ingest_data(self, data):
        # Logic to ingest SmartPOS data
        pass