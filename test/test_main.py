# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Kopi Chatbot API is running"}


def test_chat_new_conversation():
    """Test starting a new conversation"""
    response = client.post(
        "/chat",
        json={
            "message": "I think the Earth is round"
        }
    )
    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "conversation_id" in data
    assert "messages" in data
    assert len(data["messages"]) == 2  # User + bot message

    # Check message structure
    messages = data["messages"]
    assert messages[0]["role"] == "user"
    assert messages[0]["message"] == "I think the Earth is round"
    assert messages[1]["role"] == "bot"
    assert isinstance(messages[1]["message"], str)
    assert len(messages[1]["message"]) > 0


def test_chat_continue_conversation():
    """Test continuing an existing conversation"""
    # Start a conversation
    first_response = client.post(
        "/chat",
        json={
            "message": "I believe vaccines are dangerous"
        }
    )

    conversation_id = first_response.json()["conversation_id"]

    # Continue the conversation
    second_response = client.post(
        "/chat",
        json={
            "conversation_id": conversation_id,
            "message": "What about the scientific evidence?"
        }
    )

    assert second_response.status_code == 200
    data = second_response.json()

    # Check conversation ID is preserved
    assert data["conversation_id"] == conversation_id

    # Check we have 4 messages now (2 pairs)
    assert len(data["messages"]) == 4

    # Check message history is maintained
    messages = data["messages"]
    assert messages[0]["message"] == "I believe vaccines are dangerous"
    assert messages[2]["message"] == "What about the scientific evidence?"


def test_chat_invalid_request():
    """Test chat endpoint with invalid request"""
    response = client.post(
        "/chat",
        json={}  # Missing required 'message' field
    )
    assert response.status_code == 422  # Validation error