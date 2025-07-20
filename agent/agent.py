from abc import ABC, abstractmethod
from agno.agent import RunResponse
from agno.knowledge.document import DocumentKnowledgeBase

class AgentInterface(ABC):

    @abstractmethod
    async def initialize(self, knowledge_base: DocumentKnowledgeBase) -> None:
        """Initialize the agent."""
        pass
    
    @abstractmethod
    async def get_answer(self, question: str, user_id: str) -> RunResponse:
        """Get an answer to a question."""
        pass

