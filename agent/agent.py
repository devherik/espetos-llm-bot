from abc import ABC, abstractmethod
from agno.agent import RunResponse
from agno.knowledge.document import DocumentKnowledgeBase
from pydantic import SecretStr

class AgentInterface(ABC):
    _instance = None
    _agent = None
    model = None

    @abstractmethod
    async def initialize(self,key: SecretStr, knowledge_base: DocumentKnowledgeBase) -> None:
        """Initialize the agent."""
        pass
    
    @abstractmethod
    async def get_answer(self, question: str, user_id: str) -> RunResponse:
        """Get an answer to a question."""
        pass

