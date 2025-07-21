from abc import ABC, abstractmethod
from agno.vectordb.chroma import ChromaDb

class RAGInterface(ABC):
    _instance = None
    chroma_db = None
    knowledge_base = None
    
    @abstractmethod
    async def initialize(self, chroma_db: ChromaDb) -> None:
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