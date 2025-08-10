import httpx
from fastapi import APIRouter, Depends, Request
from core.deps import get_user_request_service, get_telegram_service
from services.telegram_service import TelegramService
from services.user_request_service import UserRequestService
from utils.tools.log_tool import log_message
from core.settings import settings
from models.models import TelegramUpdate, ResponseModel


# Webhooks router
webhooks = APIRouter(prefix="/webhook", tags=["telegram", "whatsapp"])


@webhooks.post("/telegram")
async def telegram_webhook(
        update: TelegramUpdate,
        user_request_service: UserRequestService = Depends(get_user_request_service),
        telegram_service: TelegramService = Depends(get_telegram_service)
    ) -> ResponseModel:
    """
    Telegram webhook endpoint to receive updates from Telegram Bot API.

    This endpoint receives updates from Telegram when users interact with your bot.
    It processes different types of updates like messages, edited messages, etc.
    """
    try:
        log_message(f"Received Telegram update: {update.update_id}", "INFO")
        # Extract the message from different update types
        message = None
        chat = None
        if update.message:
            message = update.message
            chat = update.message.chat
        elif update.edited_message:
            message = update.edited_message
        elif update.channel_post:
            message = update.channel_post
        elif update.edited_channel_post:
            message = update.edited_channel_post
        if not message or not chat:
            log_message("No message found in update", "WARNING")
            return ResponseModel(status="ok", message="No message to process")
        # Check if the message is from a bot to prevent infinite loops
        if message.from_ and message.from_.is_bot:
            log_message(
                f"Ignoring message from bot {message.from_.id} to prevent loops", "INFO")
            return ResponseModel(status="ok", message="Bot message ignored")
        if not message.text or message.text.strip() == "":
            log_message("Empty message text, ignoring", "WARNING")
            return ResponseModel(status="ok", message="Empty message ignored")
        # Process the message (this will handle the Oracle AI integration and response)
        telegram_reply = await user_request_service.process_user_request(message.text, chat.id)
        response = await telegram_service.send_message(chat.id, telegram_reply.content)
        log_message(f"Successfully processed update {update.update_id}", "INFO")
        return ResponseModel(status="ok", message="Message processed successfully", data={"response": response})
    except Exception as e:
        log_message(f"Error processing Telegram webhook: {str(e)}", "ERROR")
        # Return 200 OK to Telegram even on errors to prevent retries
        return ResponseModel(status="error", message="Internal error occurred", data={"error": str(e)})


@webhooks.post("/whatsapp")
async def whatsapp_webhook(request: Request) -> ResponseModel:
    """
    WhatsApp webhook endpoint to receive updates from WhatsApp Business API.

    This endpoint receives updates from WhatsApp when users interact with your business account.
    It processes different types of updates like messages, status updates, etc.
    """
    try:
        log_message("Received WhatsApp update", "INFO")
        # Process WhatsApp updates here
        # For now, we will just return a success message
        return ResponseModel(status="ok", message="WhatsApp webhook received successfully")

    except Exception as e:
        log_message(f"Error processing WhatsApp webhook: {str(e)}", "ERROR")
        return ResponseModel(status="error", message="Internal error occurred", data={"error": str(e)})


@webhooks.get("/test-api")
async def test_telegram_api():
    """
    Test the Telegram Bot API connection and bot info.
    """
    try:
        if not settings.telegram_bot_token:
            return {"status": "error", "message": "No bot token configured"}
        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/getMe"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            result = response.json()
        if result.get("ok"):
            bot_info = result.get("result", {})
            return {
                "status": "success",
                "message": "Telegram API is working",
                "bot_info": {
                    "id": bot_info.get("id"),
                    "username": bot_info.get("username"),
                    "first_name": bot_info.get("first_name"),
                    "is_bot": bot_info.get("is_bot")
                }
            }
        else:
            return {
                "status": "error",
                "message": "Telegram API returned error",
                "error": result.get("description", "Unknown error")
            }

    except Exception as e:
        return {
            "status": "error",
            "message": "Failed to connect to Telegram API",
            "error": str(e)
        }


@webhooks.get("/info")
async def webhook_info():
    """
    Get information about the webhook configuration.
    Useful for debugging and monitoring.
    """
    return {
        "status": "active",
        "endpoint": "/webhook",
        "supported_updates": [
            "message",
            "edited_message",
            "channel_post",
            "edited_channel_post"
        ],
        "description": "Webhooks for Oracle Celim application"
    }
