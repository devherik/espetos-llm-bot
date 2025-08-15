from core.settings import settings
from routers.webhooks import webhooks
from routers.health import router as health_router
from utils.tools.log_tool import log_message
from services.knowledge_service import KnowledgeService
from services.telegram_service import TelegramService
from services.user_request_service import UserRequestService
from core.deps import get_knowledge_service, get_telegram_service, get_user_request_service
from fastapi import FastAPI, Depends
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
app.include_router(webhooks, dependencies=[
    Depends(get_knowledge_service),
    Depends(get_user_request_service),
    Depends(get_telegram_service)
])
app.include_router(health_router)


async def startup_event(app: FastAPI) -> None:
    """
    Startup event handler to initialize resources.
    """
    log_message("Application is starting up...", "INFO")
    # Additional startup tasks can be added here
    try:
        app.state.knowledge_service = KnowledgeService()
        await app.state.knowledge_service.process_knowledge()
        app.state.user_request_service = UserRequestService()
        await app.state.user_request_service.initialize(app.state.knowledge_service)
        app.state.public_url = await start_ngrok_tunnel(port="8000", bind_tls=True)
        if not app.state.public_url:
            raise Exception("Failed to start ngrok tunnel.")
        app.state.telegram_service = TelegramService()
        await app.state.telegram_service.initialize(
            token=settings.telegram_bot_token,
            webhook_url=f"{app.state.public_url}/webhook/telegram"
        )
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
        if hasattr(app.state, 'ngrok_data') and app.state.ngrok_data:
            ngrok.disconnect(app.state.ngrok_data.public_url)
            log_message("ngrok tunnel disconnected.", "INFO")
    except Exception as e:
        log_message(f"Error during ngrok disconnection: {e}", "ERROR")
    log_message("Application shutdown complete.", "INFO")


async def start_ngrok_tunnel(port: str = "8000", bind_tls: bool = True) -> Optional[str]:
    """
    Start an ngrok tunnel to expose the application.
    """
    if settings.ENVIRONMENT == "production":
        log_message("Skipping ngrok tunnel in production environment.", "INFO")
        return None
    try:
        ngrok_auth_token = settings.ngrok_auth_token
        if ngrok_auth_token:
            conf.get_default().auth_token = ngrok_auth_token

        app.state.ngrok_data = ngrok.connect(port, bind_tls=bind_tls)
        log_message(
            f"ngrok tunnel opened at: {app.state.ngrok_data.public_url}", "SUCCESS")
        return app.state.ngrok_data.public_url
    except Exception as e:
        log_message(f"Failed to start ngrok tunnel: {e}", "ERROR")
        return None
