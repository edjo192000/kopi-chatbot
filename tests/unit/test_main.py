# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.redis_service import redis_service
from app.models.chat_models import Message
import json
import uuid

client = TestClient(app)


def test_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "redis_status" in data
    assert data["message"] == "Kopi Chatbot API v2.0 is running"


def test_health_endpoint():
    """Test the detailed health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert "version" in data
    assert "redis" in data
    assert "settings" in data
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0"


def test_stats_endpoint():
    """Test the stats endpoint"""
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()

    assert "total_conversations" in data
    assert "redis_status" in data
    assert "system_info" in data
    assert isinstance(data["total_conversations"], int)


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

    # Verify conversation ID is a valid UUID
    try:
        uuid.UUID(data["conversation_id"])
    except ValueError:
        pytest.fail("Conversation ID is not a valid UUID")


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


def test_chat_empty_message():
    """Test chat endpoint with empty message"""
    response = client.post(
        "/chat",
        json={"message": ""}
    )
    assert response.status_code == 422  # Validation error


def test_chat_very_long_message():
    """Test chat endpoint with very long message"""
    long_message = "a" * 2001  # Exceeds max length
    response = client.post(
        "/chat",
        json={"message": long_message}
    )
    assert response.status_code == 422  # Validation error


def test_delete_conversation_existing():
    """Test deleting an existing conversation"""
    # Create a conversation first
    chat_response = client.post(
        "/chat",
        json={"message": "Test message for deletion"}
    )
    conversation_id = chat_response.json()["conversation_id"]

    # Delete the conversation
    delete_response = client.delete(f"/conversations/{conversation_id}")
    assert delete_response.status_code == 200

    data = delete_response.json()
    assert "message" in data
    assert conversation_id in data["message"]


def test_delete_conversation_nonexistent():
    """Test deleting a non-existent conversation"""
    fake_id = str(uuid.uuid4())
    response = client.delete(f"/conversations/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_redis_service_connection():
    """Test Redis service connection"""
    # This test checks if Redis service can connect
    # It should pass regardless of Redis availability but log the status
    is_connected = redis_service.is_connected()
    assert isinstance(is_connected, bool)


@pytest.mark.asyncio
async def test_redis_service_operations():
    """Test Redis service basic operations"""
    if not redis_service.is_connected():
        pytest.skip("Redis not available for testing")

    # Test saving and retrieving a conversation
    test_conversation_id = f"test_{uuid.uuid4()}"
    test_messages = [
        Message(role="user", message="Test user message"),
        Message(role="bot", message="Test bot response")
    ]

    # Save conversation
    save_success = redis_service.save_conversation(test_conversation_id, test_messages)
    assert save_success == True

    # Retrieve conversation
    retrieved_messages = redis_service.get_conversation(test_conversation_id)
    assert retrieved_messages is not None
    assert len(retrieved_messages) == 2
    assert retrieved_messages[0].role == "user"
    assert retrieved_messages[0].message == "Test user message"
    assert retrieved_messages[1].role == "bot"
    assert retrieved_messages[1].message == "Test bot response"

    # Clean up
    delete_success = redis_service.delete_conversation(test_conversation_id)
    assert delete_success == True


def test_different_topic_responses():
    """Test bot responds differently to different topics"""
    topics = [
        ("I think vaccines are safe", "vaccine"),
        ("The Earth is round", "flat"),
        ("Climate change is real", "climate"),
        ("Bitcoin is the future", "crypto")
    ]

    responses = []
    for message, expected_keyword in topics:
        response = client.post("/chat", json={"message": message})
        assert response.status_code == 200

        data = response.json()
        bot_message = data["messages"][1]["message"].lower()
        responses.append(bot_message)

        # Verify bot takes a stance (response contains topic-related keywords)
        assert any(keyword in bot_message for keyword in [expected_keyword, "believe", "evidence"])

    # Verify responses are different (not just generic)
    unique_responses = set(responses)
    assert len(unique_responses) > 1, "Bot should give different responses for different topics"


def test_conversation_persistence_across_requests():
    """Test that conversation state persists across multiple requests"""
    # Start conversation
    response1 = client.post("/chat", json={"message": "Start topic"})
    conversation_id = response1.json()["conversation_id"]

    # Continue conversation multiple times
    messages = ["Continue 1", "Continue 2", "Continue 3"]

    for i, message in enumerate(messages):
        response = client.post("/chat", json={
            "conversation_id": conversation_id,
            "message": message
        })
        assert response.status_code == 200
        data = response.json()

        # Check conversation ID remains the same
        assert data["conversation_id"] == conversation_id

        # Check message count increases correctly
        expected_count = 2 + (i + 1) * 2  # Initial 2 + each round adds 2
        assert len(data["messages"]) == expected_count

        # Check latest user message is correct
        assert data["messages"][-2]["message"] == message
        assert data["messages"][-2]["role"] == "user"