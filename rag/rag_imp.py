import os
from rag.rag import RAGInterface
from agno.knowledge.document import DocumentKnowledgeBase
from agno.vectordb.chroma import ChromaDb
from agno.document.base import Document
from agno.embedder.google import GeminiEmbedder
from agno.knowledge.document import DocumentKnowledgeBase
from sqlalchemy import text, Connection, Engine, create_engine
from typing import Optional, List
from utils.logger import log_message


class RAGImp(RAGInterface):
    """Singleton class for data ingestion using ChromaDB."""
    _instance: Optional[RAGInterface] = None
    _database = None
    knowledge_base: Optional[DocumentKnowledgeBase] = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self) -> None:
        try:
            self._database = ChromaDb(
                collection="document_collection",
                path="my_chroma_db",
                persistent_client=True,
                embedder=GeminiEmbedder(api_key=os.getenv("GOOGLE_API_KEY", "")),
            )
            await self._process_data()
        except Exception as e:
            log_message(f"Error initializing ChromaDB client: {e}", "ERROR")
            return

    async def _process_data(self) -> None:
        """Process and store documents in ChromaDB."""
        try:
            if self._database is None:
                log_message("Database not initialized", "ERROR")
                return
            
            # The 'documents' list already contains the correct Document objects.
            # No need to create new ones.
            self.knowledge_base = DocumentKnowledgeBase(
                vector_db=self._database)
            
            # The load method will handle embedding and storing the documents.
            self.knowledge_base.load(recreate=False)

            log_message(f"Successfully created knowledge base.", "SUCCESS")

        except Exception as e:
            log_message(f"Error creating knowledge base: {e}", "ERROR")

    async def close(self) -> None:
        """Close the knowledge service."""
        try:
            if self._database is not None:
                # ChromaDB doesn't require explicit closing, but we can clear the reference
                self._database = None
                log_message("Data ingestor closed successfully", "INFO")
        except Exception as e:
            log_message(f"Error closing data ingestor: {e}", "ERROR")
