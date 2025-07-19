import os
from data_ingestor.data_ingestor import DataIngestorInterface
from agno.knowledge.document import DocumentKnowledgeBase
from agno.vectordb.chroma import ChromaDb
from agno.document.base import Document
from agno.embedder.google import GeminiEmbedder
from sqlalchemy import text, Connection, Engine, create_engine
from typing import Optional, List
from utils.logger import log_message


class DataIngestor(DataIngestorInterface):
    """Singleton class for data ingestion using ChromaDB."""
    _instance: Optional[DataIngestorInterface] = None
    _database = None

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
            documents = await self._load_data()
            await self._process_data(documents)
        except Exception as e:
            log_message(f"Error initializing ChromaDB client: {e}", "ERROR")
            return

    async def _load_data(self) -> List[Document]:
        """Load documents from MariaDB database."""
        documents = []
        try:
            engine_path = "mariadb+mariadbconnector://root_user:The4nerazurri@localhost/espetosdb"
            engine = create_engine(engine_path)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM Documents"))
                rows = result.fetchall()

                for row in rows:
                    # Assuming the documents table has columns like: id, title, content, metadata
                    # Adjust these column names based on your actual database schema
                    document = Document(
                        content=row[2] if len(row) > 2 else str(
                            row),  # Assuming content is 3rd column
                        id=str(row[0]) if len(row) > 0 else None,
                        name=row[1] if len(row) > 1 else None,
                        meta_data={
                            "source": "database",
                            "table": "documents"
                        }
                    )
                    documents.append(document)

                log_message(
                    f"{len(documents)} documents loaded from database", "INFO")
                return documents

        except Exception as e:
            log_message(f"Error loading data from database: {e}", "ERROR")
            return []

    async def _process_data(self, documents: List[Document]) -> None:
        """Process and store documents in ChromaDB."""
        try:
            if not documents:
                log_message("No documents to process", "WARNING")
                return

            if self._database is None:
                log_message("Database not initialized", "ERROR")
                return

            log_message(f"Processing {len(documents)} documents...", "INFO")
            
            # The 'documents' list already contains the correct Document objects.
            # No need to create new ones.
            self.knowledge_base = DocumentKnowledgeBase(
                vector_db=self._database, documents=documents)
            
            # The load method will handle embedding and storing the documents.
            self.knowledge_base.load(recreate=False)
            
            log_message(f"Successfully processed and stored {len(documents)} documents.", "SUCCESS")

        except Exception as e:
            log_message(f"Error processing documents: {e}", "ERROR")

    async def reload_data(self) -> None:
        """Reload the data from the source."""
        try:
            log_message("Reloading data from database...", "INFO")
            documents = await self._load_data()
            await self._process_data(documents)
        except Exception as e:
            log_message(f"Error reloading data: {e}", "ERROR")

    async def close(self) -> None:
        """Close the knowledge service."""
        try:
            if self._database is not None:
                # ChromaDB doesn't require explicit closing, but we can clear the reference
                self._database = None
                log_message("Data ingestor closed successfully", "INFO")
        except Exception as e:
            log_message(f"Error closing data ingestor: {e}", "ERROR")
