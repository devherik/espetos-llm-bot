import threading
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.knowledge.document import DocumentKnowledgeBase
from agno.knowledge.combined import CombinedKnowledgeBase
from agno.vectordb.pgvector import PgVector, SearchType
from typing import Optional
from utils.tools.log_tool import log_message
from utils.handlers.to_agnodoc_handler import to_agnodoc_helper
from core.settings import settings
from langchain_community.document_loaders import NotionDBLoader

class KnowledgeService:
    _instance: Optional["KnowledgeService"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls, ):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    async def process_knowledge(self) -> None:
        """
        Initializes the knowledge bases for the application.
        """
        try:
            self.pdf_knowledge = await self.get_pdf_knowledge()
            self.document_knowledge = await self.get_notion_knowledge()
            self.combined_knowledge = CombinedKnowledgeBase(
                sources=[self.pdf_knowledge, self.document_knowledge],
                vector_db=PgVector(
                    table_name="combined_knowledge",
                    db_url=settings.db_url,
                    embedder=settings.embedder,
                    search_type=SearchType.hybrid
                )
            )
        except Exception as e:
            log_message(f"Error initializing knowledge bases: {e}", "ERROR")
    
    async def get_pdf_knowledge(self) -> PDFKnowledgeBase:
        """
        Retrieves a PDF knowledge base using the provided PgVector database.
        """
        knowledge_base: PDFKnowledgeBase = PDFKnowledgeBase()
        try:
            knowledge_base = PDFKnowledgeBase(
                path="./data/new",
                vector_db=PgVector(
                    table_name="pdf_knowledge",
                    db_url=settings.db_url,
                    embedder=settings.embedder
                )
            )
            await knowledge_base.aload(recreate=False, upsert=True)
        except Exception as e:
            log_message(f"Error loading PDF knowledge base: {e}", "ERROR")
            return PDFKnowledgeBase()

        return knowledge_base
    
    async def get_notion_knowledge(self) -> DocumentKnowledgeBase:
        """
        Retrieves a Notion knowledge base using the provided PgVector database.
        """
        knowledge_base: DocumentKnowledgeBase = DocumentKnowledgeBase()
        try:
            token = settings.notion_token
            database_id = settings.notion_database_id
            if not token or not database_id:
                log_message("Notion token or database ID is not set.", "ERROR")
                return knowledge_base
            documents = NotionDBLoader(
                integration_token=token,
                database_id=database_id,
                request_timeout_sec=30
            ).load()
            documents = await to_agnodoc_helper(documents)
            knowledge_base = DocumentKnowledgeBase(
                documents=documents,
                vector_db=PgVector(
                    table_name="notion_knowledge",
                    db_url=settings.db_url,
                    embedder=settings.embedder,
                    search_type=SearchType.hybrid
                )
            )
            await knowledge_base.aload(recreate=False, upsert=True)
        except Exception as e:
            log_message(f"Error loading Notion knowledge base: {e}", "ERROR")
            return DocumentKnowledgeBase()

        return knowledge_base