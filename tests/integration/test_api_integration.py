#!/usr/bin/env python3
"""
Script to test the Kopi Chatbot API functionality
Run this after starting the service to verify everything works
Usage: python3 tests/integration/test_api_integration.py
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"


def check_health():
    """Test the root endpoint"""
    print("🔍 Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the API. Make sure the service is running.")
        return False


def check_detailed_health():
    """Test the detailed health endpoint"""
    print("\n🔍 Testing detailed health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Detailed health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Redis status: {data.get('redis', {}).get('status', 'unknown')}")
            print(f"   Active conversations: {data.get('redis', {}).get('conversations', 0)}")
            return True
        else:
            print(f"❌ Detailed health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error in detailed health check: {e}")
        return False


def check_new_conversation():
    """Test starting a new conversation"""
    print("\n🔍 Testing new conversation...")
    try:
        payload = {
            "message": "I think the Earth is round"
        }
        response = requests.post(f"{BASE_URL}/chat", json=payload)

        if response.status_code == 200:
            data = response.json()
            print("✅ New conversation test passed")
            print(f"   Conversation ID: {data.get('conversation_id')}")
            print(f"   Messages count: {len(data.get('messages', []))}")
            print(f"   Bot response: {data['messages'][-1]['message'][:100]}...")
            return data.get('conversation_id')
        else:
            print(f"❌ New conversation test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error in new conversation test: {e}")
        return None


def check_continue_conversation(conversation_id):
    """Test continuing a conversation"""
    print("\n🔍 Testing conversation continuation...")
    try:
        payload = {
            "conversation_id": conversation_id,
            "message": "But what about satellite images showing Earth's curvature?"
        }
        response = requests.post(f"{BASE_URL}/chat", json=payload)

        if response.status_code == 200:
            data = response.json()
            print("✅ Conversation continuation test passed")
            print(f"   Same conversation ID: {data.get('conversation_id') == conversation_id}")
            print(f"   Messages count: {len(data.get('messages', []))}")
            print(f"   Bot response: {data['messages'][-1]['message'][:100]}...")
            return True
        else:
            print(f"❌ Conversation continuation test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error in conversation continuation test: {e}")
        return False


def check_different_topics():
    """Test different conversation topics"""
    print("\n🔍 Testing different topics...")

    topics = [
        ("I believe vaccines are dangerous", "vaccines"),
        ("Climate change is fake", "climate"),
        ("Bitcoin is a scam", "crypto")
    ]

    results = []

    for message, topic in topics:
        try:
            payload = {"message": message}
            response = requests.post(f"{BASE_URL}/chat", json=payload)

            if response.status_code == 200:
                data = response.json()
                bot_response = data['messages'][-1]['message']
                print(f"✅ {topic.title()} topic - Bot took stance")
                print(f"   Response preview: {bot_response[:80]}...")
                results.append(True)
            else:
                print(f"❌ {topic.title()} topic failed: {response.status_code}")
                results.append(False)

            time.sleep(0.5)  # Brief pause between requests

        except Exception as e:
            print(f"❌ Error testing {topic}: {e}")
            results.append(False)

    return all(results)


def check_stats_endpoint():
    """Test the stats endpoint"""
    print("\n🔍 Testing stats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            data = response.json()
            print("✅ Stats endpoint test passed")
            print(f"   Total conversations: {data.get('total_conversations', 0)}")
            print(f"   Redis status: {data.get('redis_status', 'unknown')}")
            return True
        else:
            print(f"❌ Stats endpoint test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error in stats endpoint test: {e}")
        return False


def check_api_documentation():
    """Test that API documentation is available"""
    print("\n🔍 Testing API documentation...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API documentation is available at /docs")
            return True
        else:
            print(f"❌ API documentation test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing API documentation: {e}")
        return False


def check_conversation_deletion():
    """Test conversation deletion"""
    print("\n🔍 Testing conversation deletion...")
    try:
        # Create a test conversation
        payload = {"message": "Test deletion"}
        response = requests.post(f"{BASE_URL}/chat", json=payload)

        if response.status_code != 200:
            print("❌ Failed to create test conversation for deletion")
            return False

        conversation_id = response.json().get('conversation_id')
        print(f"   Created test conversation: {conversation_id}")

        # Delete the conversation
        delete_response = requests.delete(f"{BASE_URL}/conversations/{conversation_id}")

        if delete_response.status_code == 200:
            print("✅ Conversation deletion test passed")
            return True
        else:
            print(f"❌ Conversation deletion failed: {delete_response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error in conversation deletion test: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting Kopi Chatbot API Tests")
    print("=" * 50)

    # Test 1: Health check
    if not check_health():
        print("\n❌ API is not responding. Please check if the service is running.")
        print("   Try: docker-compose up --build -d")
        sys.exit(1)

    # Test 2: Detailed health check
    check_detailed_health()

    # Test 3: Stats endpoint
    check_stats_endpoint()

    # Test 4: New conversation
    conversation_id = check_new_conversation()
    if not conversation_id:
        print("\n❌ New conversation test failed")
        sys.exit(1)

    # Test 5: Continue conversation
    if not check_continue_conversation(conversation_id):
        print("\n❌ Conversation continuation test failed")
        sys.exit(1)

    # Test 6: Different topics
    if not check_different_topics():
        print("\n❌ Different topics test failed")

    # Test 7: Conversation deletion
    check_conversation_deletion()

    # Test 8: API documentation
    check_api_documentation()

    print("\n" + "=" * 50)
    print("🎉 API tests completed!")
    print(f"📖 API Documentation: {BASE_URL}/docs")
    print(f"🔧 Interactive API: {BASE_URL}/redoc")
    print("\n💡 For Redis-specific tests, run: python3 tests/integration/test_redis_integration.py")


if __name__ == "__main__":
    main()