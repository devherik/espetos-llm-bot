import os
from agent.agent import AgentInterface
from agent.instruction_template import agent_instruction_template
from pydantic import SecretStr
from agno.agent import Agent, RunResponse
from agno.models.google import Gemini
from agno.memory.v2.db.redis import RedisMemoryDb
from agno.memory.v2.memory import Memory
from agno.storage.redis import RedisStorage
from agno.knowledge.document import DocumentKnowledgeBase
from typing import Optional
from utils.tools.log_tool import log_message


class GeminiAgentImp(AgentInterface):
    _instance: Optional[AgentInterface] = None
    _agent = None
    model: str = "gemini-2.5-flash"

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self, key: SecretStr, knowledge_base: DocumentKnowledgeBase) -> None:
        """Initialize the agent."""
        try:
            api_key_str = key.get_secret_value()
            memory = Memory(
                db=RedisMemoryDb(
                    prefix="memory",
                    host="localhost",
                    port=6379,
                    db=0,
                ),
                model=Gemini(id=self.model, api_key=api_key_str),
            )

            storage = RedisStorage(
                prefix="storage",
                host="localhost",
                port=6379,
                db=1,
            )

            self._agent = Agent(
                model=Gemini(id=self.model, api_key=api_key_str),
                storage=storage,
                memory=memory,
                introduction="Olá, seja bem vindo ao Espeto do Vale. Como posso te ajudar hoje?",
                instructions=agent_instruction_template,
                enable_agentic_memory=True,
                add_history_to_messages=True,
                search_knowledge=True,
                show_tool_calls=True,
                knowledge=knowledge_base
            )
            log_message("Gemini agent initialized successfully", "INFO")
        except Exception as e:
            log_message(f"Error initializing Gemini agent: {e}", "ERROR")
            raise e

    async def get_answer(self, question: str, user_id: str) -> RunResponse:
        """Get an answer to a question."""
        if not self._agent:
            log_message(
                "Agent not initialized. Please call initialize() first.", "ERROR")
            return RunResponse(content="Agent not initialized.")
        try:
            response = self._agent.run(question, user_id=user_id)
            return response
        except Exception as e:
            log_message(
                f"Error getting answer from Gemini agent: {e}", "ERROR")
            return RunResponse(content="Sorry, I couldn't get an answer.")
