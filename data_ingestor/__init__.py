"""Data ingestion module for espetos-llm-bot."""

from .mariadb_data_ingestor import MariaDBDataIngestor
from .data_ingestor import DataIngestorInterface

__all__ = ['MariaDBDataIngestor', 'DataIngestorInterface']
