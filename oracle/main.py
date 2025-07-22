import os

from dotenv import load_dotenv
from utils.logger import log_message
from data_ingestor.mariadb_data_ingestor import MariaDBDataIngestor
from rag.rag_imp import RAGImp
from telegram import Update
from messenger.telegram_messenger import TelegramMessenger
from agent.gemini_agent_imp import GeminiAgentImp
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.concurrency import asynccontextmanager
from pydantic import SecretStr
from pyngrok import ngrok, conf


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
        # Set up ngrok
        ngrok_auth_token = os.getenv("NGROK_AUTHTOKEN")
        if ngrok_auth_token:
            conf.get_default().auth_token = ngrok_auth_token
        
        # Open an HTTP tunnel on the default port 8000
        public_url = ngrok.connect("8000", bind_tls=True)
        log_message(f"ngrok tunnel opened at: {public_url}", "SUCCESS")
        
        # Set the Telegram webhook
        telegram_bot = TelegramMessenger()
        telegram_bot.initialize(token=telegram_token)
        webhook_url = f"{public_url.public_url}/telegram-webhook/{telegram_token}"
        
        log_message(f"Setting Telegram webhook to: {webhook_url}", "INFO")
        
        if telegram_bot.bot:
            await telegram_bot.bot.bot.set_webhook(url=webhook_url)
            log_message(f"Telegram webhook set to: {webhook_url}", "SUCCESS")
        else:
            log_message("Telegram bot not initialized, cannot set webhook.", "ERROR")

        # Initialize the database
        database = MariaDBDataIngestor()
        await database.initialize()
        
        if database.chroma_db is None:
            log_message("ChromaDB is not initialized. Please check the data ingestion process.", "ERROR")
            return
        
        # Initialize the RAG system
        rag = RAGImp()
        await rag.initialize(chroma_db=database.chroma_db)

        if not rag.knowledge_base:
            log_message("Knowledge base is not initialized. Please check the data ingestion process.", "ERROR")
            return
            
        # Initialize the agent
        agent = GeminiAgentImp()
        await agent.initialize(key=google_api_key, knowledge_base=rag.knowledge_base)
        
        # Initialize the Telegram bot but do not run it in a blocking way
        telegram_bot = TelegramMessenger()
        telegram_bot.initialize(token=telegram_token)
        # telegram_bot.run() # This is blocking and conflicts with FastAPI's event loop

        # Store services in app.state for later use in webhook
        app.state.telegram_bot = telegram_bot
        app.state.agent = agent
        app.state.database = database
        app.state.rag = rag
        log_message("Application startup completed successfully.", "SUCCESS")

    except Exception as e:
        log_message(f"Error during initialization: {e}", "ERROR")
        # In a real app, you might want to handle this more gracefully
        raise

async def shutdown_event(app: FastAPI) -> None:
    # Perform shutdown tasks here, like closing connections or saving state
    log_message("Application is shutting down...", "INFO")
    # Disconnect ngrok
    ngrok.disconnect(public_url=app.state.public_url)
    log_message("ngrok tunnel closed.", "INFO")
    app.state.some_resource = None


@app.get("/")
async def read_root(request: Request):
    await database.reload_data()
    return {
        "message": "Welcome to the Oracle API",
        "resource": request.app.state.some_resource
    }
    
@app.get("/health")
async def health_check():
    try:
        if not database.chroma_db:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="ChromaDB is not initialized.")
        return {"status": "ok", "message": "Service is healthy"}
    except Exception as e:
        log_message(f"Health check failed: {e}", "ERROR")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    
@app.post(f"/telegram-webhook/{telegram_token}")
async def send_message(request: Request):
    try:
        agent: GeminiAgentImp = request.app.state.agent
        telegram_bot: TelegramMessenger = request.app.state.telegram_bot
        
        if not agent or not telegram_bot or not telegram_bot.bot:
            log_message("Agent or Telegram bot not initialized. Please check the startup process.", "ERROR")
            raise HTTPException(status_code=500, detail="Service not initialized.")
        
        update_json = await request.json()
        update = Update.de_json(update_json, telegram_bot.bot.bot)

        if update.message and update.message.text:
            message = update.message.text
            chat_id = str(update.message.chat_id)
            
            # Correctly call get_answer with 'question' parameter
            response = await agent.get_answer(question=message, user_id=chat_id)
            
            if response and response.content:
                await update.message.reply_text(response.content)
            else:
                await update.message.reply_text("Sorry, I couldn't get a response from the agent.")
        else:
            log_message("Update message or text is None, cannot process message.", "WARNING")
            
        return {"status": "success", "message": "Message processed successfully"}
    except Exception as e:
        log_message(f"Error processing Telegram message: {e}", "ERROR")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")
