import os

from dotenv import load_dotenv
from data_ingestor.data_ingestor import DataIngestorInterface
from handlers.metadata_handler import metadata_handler
from agno.knowledge.document import DocumentKnowledgeBase
from agno.vectordb.chroma import ChromaDb
from agno.document.base import Document as AgnoDocument
from agno.embedder.google import GeminiEmbedder
from typing import List, Optional
from langchain_community.document_loaders import NotionDBLoader
from langchain_core.documents.base import Document
from utils.logger import log_message

class NotionDataIngestor(DataIngestorInterface):
    _instance: Optional[DataIngestorInterface] = None
    chroma_db: Optional[ChromaDb] = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        super().__init__()
        log_message("NotionDataIngestor initialized", "INFO")

    async def initialize(self) -> None:
        """Initialize the knowledge service."""
        try:
            self.chroma_db = ChromaDb(
                collection="document_collection",
                path="my_chroma_db",
                persistent_client=True,
                embedder=GeminiEmbedder(api_key=os.getenv("GOOGLE_API_KEY", "")),
            )
            documents = await self._load_data()
            await self._process_data(documents)
        except Exception as e:
            log_message(f"Error initializing ChromaDb client: {e}", "ERROR")
            return

    async def _load_data(self) -> List[Document]:
        """Load data from Notion."""
        try:
            token = os.getenv("NOTION_TOKEN")
            id = os.getenv("NOTION_DATABASE_ID")
            if not token or not id:
                raise ValueError("NOTION_TOKEN and NOTION_ID environment variables must be set.")
            loader = NotionDBLoader(integration_token=token, database_id=id, request_timeout_sec=30)
            documents = loader.load()
            if not documents:
                raise ValueError("No documents found in the Notion database.")
            log_message(f"Loaded {len(documents)} documents from Notion.", "DEBUG")
            return documents
        except ValueError as e:
            log_message(f"Error loading Notion data: {e}", "ERROR")
            return []
        finally:
            log_message("Finished loading Notion data.", "SUCCESS")

    async def _process_data(self, documents: List[Document]) -> None:
        """Process the loaded Notion data."""
        try:
            agno_documents: list[AgnoDocument] = []
            if not documents:
                raise ValueError("No documents to process.")
            for doc in documents:
                cleaned_meta = {}
                if doc.metadata:
                    cleaned_meta = metadata_handler(doc.metadata)
                    agno_doc = AgnoDocument(
                        id=doc.id,
                        content=doc.page_content,
                        meta_data=cleaned_meta
                    )
                    agno_documents.append(agno_doc)
            self.knowledge_base = DocumentKnowledgeBase(vector_db=self.chroma_db, documents=agno_documents)
            self.knowledge_base.load(recreate=False)
            log_message(f"Successfully processed and stored {len(agno_documents)} documents.", "SUCCESS")
        except Exception as e:
            log_message(f"Error processing Notion data: {e}", "ERROR")
        finally:
            log_message("Finished processing Notion data.", "SUCCESS")
            
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
            if self.chroma_db is not None:
                # ChromaDB doesn't require explicit closing, but we can clear the reference
                self.chroma_db = None
                log_message("Data ingestor closed successfully", "INFO")
        except Exception as e:
            log_message(f"Error closing data ingestor: {e}", "ERROR")