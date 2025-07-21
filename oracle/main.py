import os

from dotenv import load_dotenv
from utils.logger import log_message
from data_ingestor.mariadb_data_ingestor import MariaDBDataIngestor
from rag.rag_imp import RAGImp
from messenger.telegram_messenger import TelegramMessenger
from agent.gemini_agent_imp import GeminiAgentImp
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.concurrency import asynccontextmanager
from pydantic import SecretStr


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, '.env')

if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print(f"Warning: .env file not found at {env_path}")

google_api_key = SecretStr(os.getenv("GOOGLE_API_KEY", ""))
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize resources or connections here if needed
    await startup_event(app)
    yield
    await shutdown_event(app)
    # Clean up resources or connections here if needed

app = FastAPI(lifespan=lifespan)
database = MariaDBDataIngestor()


async def startup_event(app: FastAPI) -> None:
    # Perform startup tasks here, like loading models or initializing services
    log_message("Application is starting up...", "INFO")
    try:
        database = MariaDBDataIngestor()
        await database.initialize()
        
        if database.chroma_db is None:
            print("ChromaDB is not initialized. Please check the data ingestion process.")
            return
        
        rag = RAGImp()
        await rag.initialize(chroma_db=database.chroma_db)

        if not rag.knowledge_base:
            print("Knowledge base is not initialized. Please check the data ingestion process.")
            return
        agent = GeminiAgentImp()
        await agent.initialize(key=google_api_key, knowledge_base=rag.knowledge_base)
        
        telegram_bot = TelegramMessenger()
        telegram_bot.initialize(token=telegram_token)
        telegram_bot.run()
        
    except Exception as e:
        log_message(f"Error during initialization: {e}", "ERROR")
        return
    app.state.some_resource = "Resource Initialized"


async def shutdown_event(app: FastAPI) -> None:
    # Perform shutdown tasks here, like closing connections or saving state
    log_message("Application is shutting down...", "INFO")
    app.state.some_resource = None


@app.get("/")
async def read_root(request: Request):
    await database.reload_data()
    return {
        "message": "Welcome to the Oracle API",
        "resource": request.app.state.some_resource
    }
