from pydantic import BaseModel
from core.settings import settings
from agno.embedder.openai import OpenAIEmbedder
from agno.models.google import Gemini

class AgentSettings(BaseModel):
    gemini_api_key: str = settings.google_api_key
    gemini_model: Gemini = Gemini(
        id= "gemini-2.5-flash",
        api_key=gemini_api_key
    )
    embedder: OpenAIEmbedder = OpenAIEmbedder()
    temperature: float = 0.2

    class Config:
        env_file = settings.env_path
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = 'ignore'