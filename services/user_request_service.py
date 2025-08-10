import threading
from typing import Optional

class UserRequestService:
    _instance: Optional["UserRequestService"] = None
    _lock: threading.Lock = threading.Lock()
    
    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    async def process_user_request(self, user_input: str, chat_id: int, sender_from: str) -> str:
        """
        Process user requests and generate appropriate responses.
        """
        # Here you would implement the logic to handle user requests
        # For now, let's just echo the user input
        return f"Processed request: {user_input}"