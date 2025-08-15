from fastapi import Request, HTTPException, status
from services.knowledge_service import KnowledgeService
from services.telegram_service import TelegramService
from services.user_request_service import UserRequestService

def get_knowledge_service(request: Request) -> KnowledgeService:
    """
    Dependency function to get the KnowledgeService instance from the app state.
    """
    if not hasattr(request.app.state, 'knowledge_service'):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Knowledge service is not available."
        )
    return request.app.state.knowledge_service

def get_telegram_service(request: Request) -> TelegramService:
    """
    Dependency function to get the TelegramService instance from the app state.
    """
    if not hasattr(request.app.state, 'telegram_service'):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram service is not available."
        )
    return request.app.state.telegram_service

def get_user_request_service(request: Request) -> UserRequestService:
    """
    Dependency function to get the UserRequestService instance from the app state.
    """
    if not hasattr(request.app.state, 'user_request_service'):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User request service is not available."
        )
    return request.app.state.user_request_service
