import threading
from typing import Optional
from agno.agent import Agent
from agno.memory.v2.memory import Memory
from agno.memory.v2.db.redis import RedisMemoryDb
from agno.storage.redis import RedisStorage
from utils.tools.log_tool import log_message
from core.settings import settings
from services.knowledge_service import KnowledgeService
from models.agent_models import RunResponse
from agno.models.google import Gemini

class UserRequestService:
    _instance: Optional["UserRequestService"] = None
    _lock: threading.Lock = threading.Lock()
    
    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self, knowledge_service: KnowledgeService) -> None:
        """Initialize the UserRequestService with the provided knowledge service."""
        try:
            self.knowledge_service = knowledge_service
            log_message("UserRequestService initialized successfully", "INFO")
        except Exception as e:
            log_message(f"Error initializing UserRequestService: {e}", "ERROR")
            raise e

    async def process_user_request(
        self,
        user_input: str,
        chat_id: int
    ) -> RunResponse:
        """
        Process user requests and generate appropriate responses.
        """
        try:
            agent = await self.get_allmight_agent(self.knowledge_service.combined_knowledge)
            response = agent.run(user_input, chat_id=chat_id)
            if not response.content:
                log_message("No content returned from agent, returning default response", "WARNING")
                return RunResponse(answer="No content available", content="")
            log_message(f"Processed user request: {user_input} -> {response.content}", "INFO")
            return RunResponse(answer=response.content, content=response.content)
        except Exception as e:
            log_message(f"Error getting allmight agent: {e}", "ERROR")
            return RunResponse(answer=f"Error processing request: {e}", content="")

    async def get_allmight_agent(self, knowledge) -> Agent:
        """
        Initializes and returns a classic agent with Gemini model.
        """
        try:
            try:
                with open("docs/agent_instructions.md", "r") as file:
                    instructions = file.read()
            except Exception as e:
                log_message(f"Error reading agent instructions: {e}", "ERROR")
                instructions = ""
            # Initialize Redis storage and memory
            memory = Memory(
                db=RedisMemoryDb(
                    prefix="session_memory",
                    host=settings.postgres_host,
                    port=6980,
                    db=0,
                ),
                model=Gemini(
                    id= "gemini-2.5-flash",
                    api_key=settings.google_api_key
                ),
            )
            storage = RedisStorage(
                prefix="celim_oracle",
                host=settings.postgres_host,
                port=6980,
                db=0,
            )
            knowledge.aload(recreate=False, upsert=False)
            agent = Agent(
                model=Gemini(
                    id= "gemini-2.5-flash",
                    api_key=settings.google_api_key
                ),
                knowledge=knowledge,
                search_knowledge=True,
                show_tool_calls=False,
                add_history_to_messages=True,
                instructions=instructions,
                storage=storage,
                memory=memory,
                enable_agentic_memory=True
            )
            return agent
        except Exception as e:
            log_message(f"Error initializing classic agent: {e}", "ERROR")
            raise RuntimeError(f"Could not initialize classic agent: {e}")