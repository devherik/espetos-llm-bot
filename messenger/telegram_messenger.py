from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

class TelegramMessenger:
    _instance = None
    _bot = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(TelegramMessenger, cls).__new__(cls)
        return cls._instance

    def initialize(self, token: str):
        self._bot = Application.builder().token(token).build()
        self._bot.add_handler(CommandHandler("start", self.start))
        self._bot.add_handler(CommandHandler("help", self.help))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        pass

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        pass
    
    def run(self):
        if not self._bot:
            raise ValueError("Bot is not initialized. Please provide a valid token.")
        try:
            self._bot.run_polling()
        except Exception as e:
            print(f"Error running Telegram bot: {e}")
            # Handle the error appropriately, e.g., log it or notify the user
            # For example, you could log it using a logging framework
            # log_message(f"Error running Telegram bot: {e}", "ERROR")