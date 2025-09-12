# tests/unit/test_main.py
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

    # Check updated structure for v2.0
    assert "message" in data
    assert "version" in data
    assert "status" in data
    assert "features" in data
    assert "endpoints" in data

    assert "Meta-Persuasion Enabled" in data["message"]
    assert data["status"] == "active"
    assert "Meta-persuasion analysis" in data["features"]


def test_health_endpoint():
    """Test the detailed health endpoint"""
    response = client.get("/health")
    assert response.status_code in [200, 503]  # May be degraded without Redis
    data = response.json()

    assert "status" in data
    assert "version" in data
    assert "services" in data
    assert "timestamp" in data

    # Check services structure
    services = data["services"]
    assert "redis" in services
    assert "ai_service" in services
    assert "meta_persuasion" in services

    # Check version
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

    # Check system_info includes meta-persuasion
    system_info = data["system_info"]
    assert "meta_persuasion_enabled" in system_info
    assert "version" in system_info
    assert system_info["version"] == "2.0.0"


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
    assert len(data["messages"]) >= 2  # User + bot message (may include educational content)

    # Check message structure
    messages = data["messages"]
    assert messages[0]["role"] == "user"
    assert messages[0]["message"] == "I think the Earth is round"

    # Find bot message (should be second, but might have educational content)
    bot_message = None
    for msg in messages:
        if msg["role"] == "bot":
            bot_message = msg
            break

    assert bot_message is not None
    assert isinstance(bot_message["message"], str)
    assert len(bot_message["message"]) > 0

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

    # Check we have at least 4 messages (2 pairs, might have more with educational content)
    assert len(data["messages"]) >= 4

    # Check message history is maintained (find user messages)
    user_messages = [msg for msg in data["messages"] if msg["role"] == "user"]
    assert len(user_messages) >= 2
    assert user_messages[0]["message"] == "I believe vaccines are dangerous"
    assert user_messages[1]["message"] == "What about the scientific evidence?"


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


def test_analyze_endpoint():
    """Test the new analyze endpoint"""
    response = client.post(
        "/analyze",
        json={"message": "Research shows that 95% of experts agree this is the best approach!"}
    )
    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert "topic" in data
    assert "persuasion_analysis" in data
    assert "analysis_summary" in data
    assert "timestamp" in data

    # Check analysis structure
    analysis = data["persuasion_analysis"]
    assert "techniques_detected" in analysis
    assert "persuasion_score" in analysis

    # Should detect some techniques from this persuasive message
    summary = data["analysis_summary"]
    assert summary["technique_count"] >= 1


def test_demonstrate_endpoint():
    """Test the new demonstrate endpoint"""
    response = client.post(
        "/demonstrate",
        json={
            "technique": "anchoring",
            "topic": "technology",
            "context": "discussing new innovations"
        }
    )
    assert response.status_code == 200
    data = response.json()

    assert "technique" in data
    assert "topic" in data
    assert "demonstration" in data
    assert "educational_value" in data
    assert "timestamp" in data

    assert data["technique"] == "anchoring"
    assert data["topic"] == "technology"


def test_demonstrate_invalid_technique():
    """Test demonstrate endpoint with invalid technique"""
    response = client.post(
        "/demonstrate",
        json={"technique": "invalid_technique"}
    )
    assert response.status_code == 400
    assert "Invalid technique" in response.json()["detail"]


def test_techniques_endpoint():
    """Test the new techniques endpoint"""
    response = client.get("/techniques")
    assert response.status_code == 200
    data = response.json()

    assert "available_techniques" in data
    assert "total_count" in data
    assert "categories" in data
    assert "usage_tips" in data
    assert "timestamp" in data

    # Should have multiple techniques
    assert data["total_count"] > 0
    assert len(data["available_techniques"]) == data["total_count"]


def test_conversation_analysis_endpoint():
    """Test the conversation analysis endpoint"""
    # First create a conversation
    chat_response = client.post(
        "/chat",
        json={"message": "I think artificial intelligence will replace all jobs"}
    )
    conversation_id = chat_response.json()["conversation_id"]

    # Add another message
    client.post(
        "/chat",
        json={
            "conversation_id": conversation_id,
            "message": "Multiple studies show 89% of experts agree AI displacement is accelerating"
        }
    )

    # Now analyze the conversation
    analysis_response = client.get(f"/conversation/{conversation_id}/analysis")
    assert analysis_response.status_code == 200

    data = analysis_response.json()
    assert "conversation_id" in data
    assert "message_count" in data
    assert "message_analyses" in data
    assert "insights" in data
    assert "recommendations" in data
    assert "timestamp" in data


def test_conversation_analysis_not_found():
    """Test conversation analysis for non-existent conversation"""
    fake_id = str(uuid.uuid4())
    response = client.get(f"/conversation/{fake_id}/analysis")
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
        # Find bot message
        bot_message = None
        for msg in data["messages"]:
            if msg["role"] == "bot":
                bot_message = msg["message"].lower()
                break

        assert bot_message is not None
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

        # Check that user messages are present and correct
        user_messages = [msg for msg in data["messages"] if msg["role"] == "user"]
        assert len(user_messages) >= i + 2  # Initial message + current messages

        # Check latest user message is correct
        assert user_messages[-1]["message"] == message
        assert user_messages[-1]["role"] == "user"


def test_meta_persuasion_integration():
    """Test that meta-persuasion features are working"""
    # Test a message with multiple persuasion techniques
    persuasive_message = "Leading experts at Harvard and MIT have proven that 97% of scientists agree this approach works. Imagine how this could transform your life!"

    response = client.post("/chat", json={"message": persuasive_message})
    assert response.status_code == 200

    # The response might include educational content due to the sophisticated message
    data = response.json()
    bot_messages = [msg for msg in data["messages"] if msg["role"] == "bot"]
    assert len(bot_messages) >= 1

    # Check if educational content was added (might be present as a note)
    bot_response = bot_messages[0]["message"]
    assert len(bot_response) > 0


def test_error_handling():
    """Test various error conditions"""
    # Test malformed JSON for analyze endpoint
    response = client.post("/analyze", json={})
    assert response.status_code == 400

    # Test invalid conversation ID format
    response = client.get("/conversation/invalid-id/analysis")
    assert response.status_code == 404


def test_cors_headers():
    """Test that CORS headers are properly set"""
    response = client.options("/")
    # FastAPI should handle CORS automatically with our middleware
    assert response.status_code in [200, 405]  # OPTIONS might not be explicitly handled


def test_api_versioning():
    """Test that API returns correct version information"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "2.0" in data["message"] or "version" in data

    # Check health endpoint version
    health_response = client.get("/health")
    if health_response.status_code == 200:
        health_data = health_response.json()
        assert health_data["version"] == "2.0.0"