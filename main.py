import asyncio
import os

from data_ingestor.data_ingestor_imp import DataIngestor
from agent.gemini_agent_imp import GeminiAgentImp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, '.env')

async def main():
    database = DataIngestor()
    await database.initialize()

    if not database.knowledge_base:
        print("Knowledge base is not initialized. Please check the data ingestion process.")
        return
    agent = GeminiAgentImp()
    await agent.initialize(knowledge_base=database.knowledge_base)
    
    response = await agent.get_answer("What is the capital of France?", user_id="12345")
    print(f"Response: {response.content}")

if __name__ == "__main__":
    asyncio.run(main())