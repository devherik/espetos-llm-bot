from abc import ABC, abstractmethod

class AgentInterface(ABC):

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent."""
        pass

