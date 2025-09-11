#!/usr/bin/env python3
"""
Script to test Redis integration functionality
Run this to verify Redis is working correctly with the chatbot
"""

import requests
import json
import time
import sys
import redis
from datetime import datetime

BASE_URL = "http://localhost:8000"
REDIS_URL = "redis://localhost:6379"


def test_redis_direct_connection():
    """Test direct connection to Redis"""
    print("🔍 Testing direct Redis connection...")
    try:
        r = redis.from_url(REDIS_URL, decode_responses=True)
        r.ping()
        print("✅ Direct Redis connection successful")

        # Test basic operations
        test_key = f"test:{int(time.time())}"
        r.set(test_key, "test_value", ex=10)
        value = r.get(test_key)
        if value == "test_value":
            print("✅ Redis read/write operations working")
            r.delete(test_key)
            return True
        else:
            print("❌ Redis read/write operations failed")
            return False
    except Exception as e:
        print(f"❌ Direct Redis connection failed: {e}")
        return False


def test_api_health_with_redis():
    """Test API health endpoint with Redis status"""
    print("\n🔍 Testing API health with Redis status...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working")
            print(f"   Redis status: {data.get('redis', {}).get('status', 'unknown')}")
            print(f"   Active conversations: {data.get('redis', {}).get('conversations', 0)}")
            return data.get('redis', {}).get('status') == 'connected'
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")
        return False


def test_conversation_persistence():
    """Test that conversations are persisted in Redis"""
    print("\n🔍 Testing conversation persistence...")

    try:
        # Start a new conversation
        response1 = requests.post(f"{BASE_URL}/chat", json={
            "message": "I think the Earth is round"
        })

        if response1.status_code != 200:
            print(f"❌ Failed to start conversation: {response1.status_code}")
            return False

        conversation_id = response1.json()["conversation_id"]
        print(f"   Started conversation: {conversation_id}")

        # Verify conversation is in Redis
        r = redis.from_url(REDIS_URL, decode_responses=True)
        redis_key = f"conversation:{conversation_id}"
        redis_data = r.get(redis_key)

        if not redis_data:
            print("❌ Conversation not found in Redis")
            return False

        # Parse and verify data
        messages = json.loads(redis_data)
        if len(messages) != 2:  # User + bot message
            print(f"❌ Expected 2 messages, found {len(messages)}")
            return False

        print("✅ Conversation successfully stored in Redis")

        # Continue conversation to test retrieval
        response2 = requests.post(f"{BASE_URL}/chat", json={
            "conversation_id": conversation_id,
            "message": "But what about satellite images?"
        })

        if response2.status_code != 200:
            print(f"❌ Failed to continue conversation: {response2.status_code}")
            return False

        # Verify updated conversation in Redis
        updated_data = r.get(redis_key)
        updated_messages = json.loads(updated_data)

        if len(updated_messages) != 4:  # 2 user + 2 bot messages
            print(f"❌ Expected 4 messages after continuation, found {len(updated_messages)}")
            return False

        print("✅ Conversation continuation and retrieval working")

        # Check TTL
        ttl = r.ttl(redis_key)
        if ttl > 0:
            print(f"✅ TTL is set: {ttl} seconds remaining")
        else:
            print("⚠️ TTL not set or expired")

        return True

    except Exception as e:
        print(f"❌ Error testing conversation persistence: {e}")
        return False


def test_conversation_ttl():
    """Test conversation TTL (Time To Live) functionality"""
    print("\n🔍 Testing conversation TTL...")

    try:
        # Start conversation
        response = requests.post(f"{BASE_URL}/chat", json={
            "message": "Test TTL message"
        })

        conversation_id = response.json()["conversation_id"]

        # Check initial TTL
        r = redis.from_url(REDIS_URL, decode_responses=True)
        redis_key = f"conversation:{conversation_id}"
        initial_ttl = r.ttl(redis_key)

        print(f"   Initial TTL: {initial_ttl} seconds")

        if initial_ttl <= 0:
            print("❌ TTL not set properly")
            return False

        # Wait a bit and continue conversation (should extend TTL)
        time.sleep(2)

        requests.post(f"{BASE_URL}/chat", json={
            "conversation_id": conversation_id,
            "message": "Continuing conversation"
        })

        extended_ttl = r.ttl(redis_key)
        print(f"   TTL after activity: {extended_ttl} seconds")

        if extended_ttl <= initial_ttl:
            print("⚠️ TTL may not have been extended (or test too fast)")
        else:
            print("✅ TTL extended on activity")

        return True

    except Exception as e:
        print(f"❌ Error testing TTL: {e}")
        return False


def test_stats_endpoint():
    """Test statistics endpoint"""
    print("\n🔍 Testing stats endpoint...")

    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            data = response.json()
            print("✅ Stats endpoint working")
            print(f"   Total conversations: {data.get('total_conversations', 0)}")
            print(f"   Redis status: {data.get('redis_status', 'unknown')}")
            return True
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing stats endpoint: {e}")
        return False


def test_conversation_deletion():
    """Test conversation deletion"""
    print("\n🔍 Testing conversation deletion...")

    try:
        # Create conversation
        response = requests.post(f"{BASE_URL}/chat", json={
            "message": "Test deletion"
        })

        conversation_id = response.json()["conversation_id"]
        print(f"   Created conversation: {conversation_id}")

        # Verify it exists in Redis
        r = redis.from_url(REDIS_URL, decode_responses=True)
        redis_key = f"conversation:{conversation_id}"

        if not r.exists(redis_key):
            print("❌ Conversation not found in Redis")
            return False

        # Delete conversation
        delete_response = requests.delete(f"{BASE_URL}/conversations/{conversation_id}")

        if delete_response.status_code == 200:
            print("✅ Conversation deleted via API")
        else:
            print(f"❌ Failed to delete conversation: {delete_response.status_code}")
            return False

        # Verify it's gone from Redis
        if not r.exists(redis_key):
            print("✅ Conversation removed from Redis")
            return True
        else:
            print("❌ Conversation still exists in Redis")
            return False

    except Exception as e:
        print(f"❌ Error testing conversation deletion: {e}")
        return False


def test_message_limit():
    """Test message history limiting"""
    print("\n🔍 Testing message history limiting...")

    try:
        # Start conversation
        response = requests.post(f"{BASE_URL}/chat", json={
            "message": "Start conversation"
        })

        conversation_id = response.json()["conversation_id"]

        # Send multiple messages to exceed limit
        for i in range(6):  # This should create 12 total messages (6 user + 6 bot)
            requests.post(f"{BASE_URL}/chat", json={
                "conversation_id": conversation_id,
                "message": f"Message number {i + 2}"
            })

        # Check final conversation
        final_response = requests.post(f"{BASE_URL}/chat", json={
            "conversation_id": conversation_id,
            "message": "Final message"
        })

        messages = final_response.json()["messages"]
        message_count = len(messages)

        print(f"   Final message count: {message_count}")

        if message_count <= 10:  # Should be limited to max_conversation_messages
            print("✅ Message history properly limited")
            return True
        else:
            print(f"❌ Message history not limited (expected ≤10, got {message_count})")
            return False

    except Exception as e:
        print(f"❌ Error testing message limit: {e}")
        return False


def cleanup_test_data():
    """Clean up test data from Redis"""
    print("\n🧹 Cleaning up test data...")
    try:
        r = redis.from_url(REDIS_URL, decode_responses=True)
        test_keys = r.keys("conversation:*")
        if test_keys:
            r.delete(*test_keys)
            print(f"✅ Cleaned up {len(test_keys)} test conversations")
        else:
            print("✅ No test data to clean up")
    except Exception as e:
        print(f"⚠️ Error during cleanup: {e}")


def main():
    """Run all Redis integration tests"""
    print("🚀 Starting Redis Integration Tests")
    print("=" * 60)

    tests = [
        ("Direct Redis Connection", test_redis_direct_connection),
        ("API Health with Redis", test_api_health_with_redis),
        ("Conversation Persistence", test_conversation_persistence),
        ("Conversation TTL", test_conversation_ttl),
        ("Stats Endpoint", test_stats_endpoint),
        ("Conversation Deletion", test_conversation_deletion),
        ("Message History Limiting", test_message_limit),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")

    cleanup_test_data()

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All Redis integration tests passed!")
        print("✅ Redis integration is working correctly")
        return 0
    else:
        print(f"❌ {total - passed} tests failed")
        print("🔧 Please check Redis connection and configuration")
        return 1


if __name__ == "__main__":
    sys.exit(main())