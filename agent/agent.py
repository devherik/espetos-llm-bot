from abc import ABC, abstractmethod
from agno.agent import RunResponse

class AgentInterface(ABC):

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent."""
        pass
    
    @abstractmethod
    async def get_answer(self, question: str, user_id: str) -> RunResponse:
        """Get an answer to a question."""
        pass

