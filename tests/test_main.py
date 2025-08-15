import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app

client = TestClient(app)

def test_health_check_success():
    with patch('asyncpg.connect', new_callable=AsyncMock) as mock_connect:
        mock_conn = AsyncMock()
        mock_conn.fetchval.return_value = 1
        mock_connect.return_value = mock_conn
        
        with patch('redis.asyncio.Redis.ping', new_callable=AsyncMock) as mock_ping:
            mock_ping.return_value = True
            
            response = client.get("/health/")
            assert response.status_code == 200
            assert response.json() == {"status": "ok", "details": {"redis": "ok", "postgres": "ok"}}

def test_health_check_db_fails():
    with patch('asyncpg.connect', new_callable=AsyncMock) as mock_connect:
        mock_connect.side_effect = Exception("DB connection failed")
        
        with patch('redis.asyncio.Redis.ping', new_callable=AsyncMock) as mock_ping:
            mock_ping.return_value = True

            response = client.get("/health/")
            assert response.status_code == 503
            assert response.json()["details"]["postgres"] == "error"

def test_telegram_webhook_empty_message():
    # Simulate a Telegram update with no text
    update_data = {
        "update_id": 12345,
        "message": {
            "message_id": 54321,
            "date": 1678886400,
            "chat": {"id": 111, "type": "private", "first_name": "Test"},
            "from": {"id": 111, "is_bot": False, "first_name": "Test"},
            "text": ""
        }
    }
    response = client.post("/webhook/telegram", json=update_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Empty message ignored"

def test_telegram_webhook_bot_message():
    # Simulate a message from a bot
    update_data = {
        "update_id": 12345,
        "message": {
            "message_id": 54321,
            "date": 1678886400,
            "chat": {"id": 111, "type": "private", "first_name": "Test"},
            "from": {"id": 987, "is_bot": True, "first_name": "AnotherBot"},
            "text": "hello"
        }
    }
    response = client.post("/webhook/telegram", json=update_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Bot message ignored"
