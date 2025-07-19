"""Data ingestion module for espetos-llm-bot."""

from .data_ingestor_imp import DataIngestor
from .data_ingestor import DataIngestorInterface

__all__ = ['DataIngestor', 'DataIngestorInterface']
