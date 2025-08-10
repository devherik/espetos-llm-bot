from langchain_core.documents.base import Document
from agno.document.base import Document as AgnoDocument
from metadata_handler import data_handler
from utils.tools.log_tool import log_message

async def to_agnodoc_helper(documents: list[Document]) -> list[AgnoDocument]:
        """
        Converts LangChain Document objects to Agno Document objects.
        """
        agno_docs: list[AgnoDocument] = []
        try:
            for doc in documents:
                cleaned_metadata = data_handler(doc.metadata)
                agno_doc = AgnoDocument(
                    id=doc.id,
                    content=doc.page_content,
                    meta_data=cleaned_metadata
                )
                agno_docs.append(agno_doc)
            return agno_docs
        except Exception as e:
            log_message(f"Error converting documents: {e}", "ERROR")
        return agno_docs