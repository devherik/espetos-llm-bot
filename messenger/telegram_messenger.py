from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters, MessageHandler

from utils.tools.log_tool import log_message


class TelegramMessenger:
    _instance = None
    bot = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(TelegramMessenger, cls).__new__(cls)
        return cls._instance

    def initialize(self, token: str):
        try:
            self.bot = Application.builder().token(token).build()
            self.bot.add_handler(CommandHandler("start", self.start))
            self.bot.add_handler(CommandHandler("help", self.help))
            self.bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))
            # self.bot.run_polling()
            log_message("Telegram bot initialized successfully", "INFO")
        except Exception as e:
            log_message(f"Error initializing Telegram bot: {e}", "ERROR")
            raise e

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            raise ValueError("Update message is None")
        try:
            await update.message.reply_text("Welcome to the Espetos LLM Bot! How can I assist you today?")
        except Exception as e:
            print(f"Error in start command: {e}")
            await update.message.reply_text("An error occurred while processing your request. Please try again later.")

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Echo the user message."""
        if not update.message or not update.message.text:
            # This path should not be taken due to the MessageHandler filter, but it's a good practice for type safety.
            return
        try:
            await update.message.reply_text(update.message.text)
        except Exception as e:
            print(f"Error in echo command: {e}")
            await update.message.reply_text("An error occurred while processing your request. Please try again later.")

    def run(self):
        """Run the bot."""
        if not self.bot:
            log_message("Bot not initialized. Please call initialize() first.", "ERROR")
            return
        try:
            log_message("Running Telegram bot...", "INFO")
            self.bot.run_polling()
        except Exception as e:
            log_message(f"Error running Telegram bot: {e}", "ERROR")

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            raise ValueError("Update message is None")
        try:
            await update.message.reply_text("Here are some commands you can use:\n/start - Start the conversation\n/help - Get help")
        except Exception as e:
            print(f"Error in help command: {e}")
            await update.message.reply_text("An error occurred while processing your request. Please try again later.")
