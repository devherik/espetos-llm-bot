# models.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional, Dict, Any

class IngestRequest(BaseModel):
    collection: str
    source_type: Literal["local", "notion"]
    path: Optional[str] = None  # e.g., 'data/project_a' for local

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class ResponseModel(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

class TelegramUser(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None

class TelegramChat(BaseModel):
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class TelegramMessage(BaseModel):
    message_id: int
    from_: Optional[TelegramUser] = Field(None, alias="from")
    date: int
    chat: TelegramChat
    text: Optional[str] = None
    photo: Optional[list] = None
    document: Optional[Dict[str, Any]] = None
    voice: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[TelegramMessage] = None
    edited_message: Optional[TelegramMessage] = None
    channel_post: Optional[TelegramMessage] = None
    edited_channel_post: Optional[TelegramMessage] = None
    
    model_config = ConfigDict(
        extra="allow",
    )