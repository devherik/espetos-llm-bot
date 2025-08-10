import httpx
from utils.tools.log_tool import log_message

class TelegramService:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(TelegramService, cls).__new__(cls)
        return cls._instance
    
    async def initialize(self, token: str, webhook_url: str):
        """
        Initialize the Telegram service with the provided bot token.
        """
        try:
            if not token:
                raise ValueError("Telegram bot token is required")
            self.bot_token = token
            self.telegram_api_endpoint = f"https://api.telegram.org/bot{self.bot_token}"
            await self.setup_webhook(webhook_url)
            log_message("Telegram service initialized successfully", "INFO")
        except Exception as e:
            log_message(f"Error initializing Telegram service: {e}", "ERROR")
            raise e

    async def send_message(self, chat_id: int, text: str, parse_mode: str = "Markdown") -> dict:
        """
        Send a message to a Telegram chat.
        """
        try:
            log_message(f"Sending message to chat {chat_id}: {text[:50]}...", "INFO")
            url = f"{self.telegram_api_endpoint}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                if response.status_code != 200:
                    log_message(f"Failed to send message: {response.text}", "ERROR")
                    return {"status": "error", "message": response.text}
                return response.json()
        except Exception as e:
            log_message(f"Error sending Telegram message: {str(e)}", "ERROR")
            raise e


    async def setup_webhook(self, webhook_url: str):
        """Set up Telegram webhook programmatically during startup."""
        try:
            if not self.bot_token:
                log_message("No Telegram bot token configured", "WARNING")
                return
            payload = {"url": webhook_url}
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.telegram_api_endpoint}/setWebhook", json=payload)
                response.raise_for_status()
                result = response.json()
            if result.get("ok"):
                log_message(f"Telegram webhook successfully set to: {self.telegram_api_endpoint}", "INFO")
            else:
                log_message(f"Failed to set Telegram webhook: {result}", "ERROR")
        except Exception as e:
            log_message(f"Error setting up Telegram webhook: {e}", "ERROR")