from abc import ABC, abstractmethod

class RAGInterface(ABC):
    _instance = None
    _database = None
    knowledge_base = None
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the data ingestion pipeline."""
        pass
    
    @abstractmethod
    async def _process_data(self) -> None:
        """Process the loaded documents."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the knowledge service."""
        pass