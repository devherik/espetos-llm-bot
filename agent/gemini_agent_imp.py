from agent.agent import AgentInterface
from pydantic import SecretStr
from agno.agent import Agent
from agno.models.google import Gemini
from agno.memory.v2.db.redis import RedisMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.redis import RedisStorage
from agno.tools.telegram import TelegramTools
from typing import Optional
from utils.logger import log_message

class GeminiAgentImp(AgentInterface):
    _instance: Optional[AgentInterface] = None
    _agent = None
    model: str = "gemini-2.5-flash"

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    
    async def initialize(self) -> None:
        """Initialize the agent."""
        
