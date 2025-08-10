import httpx
from core.settings import settings
from utils.tools.log_tool import log_message
from services.knowledge_service import KnowledgeService
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from pyngrok import ngrok, conf
from typing import Optional

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to handle the startup and shutdown of the application.
    """
    log_message("Starting application...", "INFO")
    try:
        await startup_event(app)
        yield
    finally:
        await shutdown_event(app)
        log_message("Application shutdown complete.", "INFO")

app = FastAPI(lifespan=lifespan)

async def startup_event(app: FastAPI) -> None:
    """
    Startup event handler to initialize resources.
    """
    log_message("Application is starting up...", "INFO")
    # Additional startup tasks can be added here
    try:
        app.state.knowledge_service = KnowledgeService()
        await app.state.knowledge_service.process_knowledge()
        app.state.public_url = await start_ngrok_tunnel(port="8000", bind_tls=True)
        if not app.state.public_url: raise Exception("Failed to start ngrok tunnel.")
        await setup_telegram_webhook_programmatically(app.state.public_url + "/telegram-webhook")
    except Exception as e:
        log_message(f"Error during startup: {e}", "ERROR")
    log_message("Application startup complete.", "INFO")

async def shutdown_event(app: FastAPI) -> None:
    """
    Shutdown event handler to clean up resources.
    """
    log_message("Application is shutting down...", "INFO")
    # Additional shutdown tasks can be added here
    try:
        await app.state.ngrok_data.disconnect(app.state.public_url)
    except Exception as e:
        log_message(f"Error during shutdown: {e}", "ERROR")
    log_message("Application shutdown complete.", "INFO")

async def start_ngrok_tunnel(port: str = "8000", bind_tls: bool = True) -> Optional[str]:
    """
    Start an ngrok tunnel to expose the application.
    """
    try:
        ngrok_auth_token = settings.ngrok_auth_token
        if ngrok_auth_token:
            conf.get_default().auth_token = ngrok_auth_token
        
        app.state.ngrok_data = ngrok.connect(port, bind_tls=bind_tls)
        log_message(f"ngrok tunnel opened at: {app.state.ngrok_data.public_url}", "SUCCESS")
        return app.state.ngrok_data.public_url
    except Exception as e:
        log_message(f"Failed to start ngrok tunnel: {e}", "ERROR")
        return None
    
async def setup_telegram_webhook_programmatically(webhook_url: str):
    """Set up Telegram webhook programmatically during startup."""
    try:
        if not settings.telegram_bot_token:
            log_message("No Telegram bot token configured", "WARNING")
            return
        telegram_api_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/setWebhook"
        payload = {"url": webhook_url}
        async with httpx.AsyncClient() as client:
            response = await client.post(telegram_api_url, json=payload)
            response.raise_for_status()
            result = response.json()
        if result.get("ok"):
            log_message(f"Telegram webhook successfully set to: {webhook_url}", "INFO")
        else:
            log_message(f"Failed to set Telegram webhook: {result}", "ERROR")
    except Exception as e:
        log_message(f"Error setting up Telegram webhook: {e}", "ERROR")