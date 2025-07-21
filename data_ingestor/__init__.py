"""Data ingestion module for espetos-llm-bot."""

from .data_ingestor_imp import MariaDBDataIngestor
from .data_ingestor import DataIngestorInterface

__all__ = ['MariaDBDataIngestor', 'DataIngestorInterface']
