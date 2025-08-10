import os
from dotenv import load_dotenv
from utils.tools.log_tool import log_message
from pydantic_settings import BaseSettings
from agno.embedder.openai import OpenAIEmbedder

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, '.env')

if os.path.exists(env_path):
    load_dotenv(env_path)
    log_message(f".env file loaded from {env_path}", "INFO")
else:
    log_message(f"Warning: .env file not found at {env_path}", "WARNING")
    
class EnvironmentSettings(BaseSettings):
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    embedder: OpenAIEmbedder = OpenAIEmbedder()
    notion_token: str = os.getenv("NOTION_TOKEN", "")
    notion_database_id: str = os.getenv("NOTION_DATABASE_ID", "")
    ngrok_auth_token: str = os.getenv("NGROK_AUTH_TOKEN", "")
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_webhook_url: str = os.getenv("TELEGRAM_WEBHOOK_URL", "")
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", 5432))
    postgres_db: str = os.getenv("POSTGRES_DB", "espetos_llm_bot")
    db_url: str = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
    smart_pos_api_key: str = os.getenv("SMART_POS_API_KEY", "")
    env_path: str = env_path
    
    class Config:
        env_file = env_path
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = "ignore"
        
settings = EnvironmentSettings()
