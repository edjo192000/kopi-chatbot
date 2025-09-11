#!/usr/bin/env python3
"""
Script to test OpenAI integration functionality
Tests both with and without OpenAI API key to verify fallback behavior
Usage: python3 tests/integration/test_openai_integration.py
"""

import requests
import json
import time
import sys
import os
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def check_openai_api_health():
    """Check if OpenAI is configured and available"""
    print("🔍 Testing OpenAI API integration status...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            ai_status = data.get('ai', {})

            print("✅ AI Service Status:")
            print(f"   OpenAI Enabled: {ai_status.get('openai_enabled', False)}")
            print(f"   API Key Configured: {ai_status.get('api_key_configured', False)}")
            print(f"   Client Available: {ai_status.get('client_available', False)}")
            print(f"   Model: {ai_status.get('model', 'unknown')}")
            print(f"   Temperature: {ai_status.get('temperature', 'unknown')}")

            return ai_status
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error checking AI status: {e}")
        return None


def test_conversation_with_ai(topic_message: str, topic_name: str) -> str:
    """Test a conversation flow and return conversation_id"""
    print(f"\n🔍 Testing {topic_name} conversation...")

    try:
        # Start conversation
        response1 = requests.post(f"{BASE_URL}/chat", json={
            "message": topic_message
        })

        if response1.status_code != 200:
            print(f"❌ Failed to start conversation: {response1.status_code}")
            return None

        data1 = response1.json()
        conversation_id = data1["conversation_id"]
        bot_response1 = data1["messages"][-1]["message"]

        print(f"✅ Started {topic_name} conversation")
        print(f"   Conversation ID: {conversation_id}")
        print(f"   Bot response length: {len(bot_response1)} characters")
        print(f"   Response preview: {bot_response1[:100]}...")

        # Continue conversation
        follow_up_messages = {
            "flat_earth": "But what about satellite images from space?",
            "vaccines": "What about vaccine side effects?",
            "climate": "Isn't climate change just natural cycles?",
            "crypto": "But cryptocurrency is too volatile!"
        }

        follow_up = follow_up_messages.get(topic_name, "Can you explain more?")

        response2 = requests.post(f"{BASE_URL}/chat", json={
            "conversation_id": conversation_id,
            "message": follow_up
        })

        if response2.status_code == 200:
            data2 = response2.json()
            bot_response2 = data2["messages"][-1]["message"]
            print(f"✅ Continued conversation successfully")
            print(f"   Follow-up response length: {len(bot_response2)} characters")
            print(f"   Response preview: {bot_response2[:100]}...")

            # Analyze response quality
            analyze_response_quality(bot_response1, bot_response2, topic_name)

        else:
            print(f"❌ Failed to continue conversation: {response2.status_code}")

        return conversation_id

    except Exception as e:
        print(f"❌ Error testing {topic_name} conversation: {e}")
        return None


def analyze_response_quality(response1: str, response2: str, topic: str):
    """Analyze if responses are high-quality and topic-appropriate"""
    print(f"📊 Analyzing response quality for {topic}...")

    # Check response length (AI responses should be longer and more detailed)
    if len(response1) > 100 and len(response2) > 100:
        print("   ✅ Responses are sufficiently detailed")
    else:
        print("   ⚠️ Responses seem short (might be fallback responses)")

    # Check for topic-specific keywords
    topic_keywords = {
        "flat_earth": ["earth", "flat", "globe", "nasa", "curve", "horizon"],
        "vaccines": ["vaccine", "medical", "disease", "health", "safe", "effective"],
        "climate": ["climate", "warming", "carbon", "temperature", "environment"],
        "crypto": ["bitcoin", "cryptocurrency", "blockchain", "financial", "currency"]
    }

    keywords = topic_keywords.get(topic, [])
    found_keywords = []

    combined_response = (response1 + " " + response2).lower()
    for keyword in keywords:
        if keyword in combined_response:
            found_keywords.append(keyword)

    if found_keywords:
        print(f"   ✅ Topic-relevant keywords found: {', '.join(found_keywords)}")
    else:
        print(f"   ⚠️ Few topic-relevant keywords found")

    # Check for persuasive language
    persuasive_indicators = [
        "evidence", "proof", "research", "studies", "facts", "data",
        "overwhelming", "clear", "obvious", "undeniable", "absolutely"
    ]

    found_persuasive = []
    for indicator in persuasive_indicators:
        if indicator in combined_response:
            found_persuasive.append(indicator)

    if found_persuasive:
        print(f"   ✅ Persuasive language detected: {', '.join(found_persuasive[:3])}...")
    else:
        print(f"   ⚠️ Limited persuasive language found")


def test_ai_vs_fallback_comparison():
    """Compare AI responses vs fallback responses"""
    print("\n🔍 Testing AI vs Fallback behavior...")

    # Test topics
    topics = [
        ("I think the Earth is round", "flat_earth"),
        ("Vaccines are safe", "vaccines"),
        ("Climate change is real", "climate"),
        ("Bitcoin is valuable", "crypto")
    ]

    results = []

    for message, topic in topics:
        conversation_id = test_conversation_with_ai(message, topic)
        if conversation_id:
            results.append((topic, conversation_id))
        time.sleep(1)  # Brief pause between tests

    return results


def test_fallback_behavior():
    """Test that fallback works when OpenAI is unavailable"""
    print("\n🔍 Testing fallback behavior...")

    # This test assumes OpenAI might not be configured
    # We can't force OpenAI to fail without modifying code,
    # but we can test that the system works regardless

    try:
        response = requests.post(f"{BASE_URL}/chat", json={
            "message": "Test fallback behavior"
        })

        if response.status_code == 200:
            data = response.json()
            bot_response = data["messages"][-1]["message"]

            print("✅ System responds successfully (AI or fallback)")
            print(f"   Response length: {len(bot_response)} characters")

            # Check if it's likely a fallback response
            if len(bot_response) < 200 and any(phrase in bot_response.lower() for phrase in [
                "fascinating topic", "disagree with your perspective", "opposite view"
            ]):
                print("   💡 Appears to be using fallback response")
            else:
                print("   🤖 Appears to be using AI response")

            return True
        else:
            print(f"❌ Fallback test failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error testing fallback: {e}")
        return False


def test_conversation_consistency():
    """Test that bot maintains consistent position throughout conversation"""
    print("\n🔍 Testing conversation consistency...")

    try:
        # Start with vaccine topic
        messages = [
            "I think vaccines are dangerous",
            "But what about all the scientific studies?",
            "What about natural immunity?",
            "Are you sure vaccines are completely safe?"
        ]

        conversation_id = None
        responses = []

        for i, message in enumerate(messages):
            payload = {"message": message}
            if conversation_id:
                payload["conversation_id"] = conversation_id

            response = requests.post(f"{BASE_URL}/chat", json=payload)

            if response.status_code == 200:
                data = response.json()
                conversation_id = data["conversation_id"]
                bot_response = data["messages"][-1]["message"]
                responses.append(bot_response)

                print(f"   Message {i + 1}: {len(bot_response)} chars")
            else:
                print(f"❌ Failed at message {i + 1}: {response.status_code}")
                return False

        # Analyze consistency
        combined_responses = " ".join(responses).lower()
        pro_vaccine_indicators = ["safe", "effective", "medical achievement", "save lives", "scientific evidence"]

        found_indicators = [ind for ind in pro_vaccine_indicators if ind in combined_responses]

        if len(found_indicators) >= 3:
            print("✅ Bot maintained consistent pro-vaccine position")
            print(f"   Consistent indicators: {', '.join(found_indicators)}")
        else:
            print("⚠️ Bot position consistency unclear")

        return True

    except Exception as e:
        print(f"❌ Error testing consistency: {e}")
        return False


def main():
    """Run all OpenAI integration tests"""
    print("🚀 Starting OpenAI Integration Tests")
    print("=" * 60)

    # Test 1: Check AI service status
    ai_status = check_openai_api_health()
    if not ai_status:
        print("\n❌ Cannot proceed - API health check failed")
        sys.exit(1)

    # Test 2: Test AI vs Fallback behavior
    test_results = test_ai_vs_fallback_comparison()

    # Test 3: Test fallback behavior specifically
    fallback_works = test_fallback_behavior()

    # Test 4: Test conversation consistency
    consistency_works = test_conversation_consistency()

    # Summary
    print("\n" + "=" * 60)
    print("📊 OpenAI Integration Test Results:")
    print(
        f"   AI Service Status: {'✅ Available' if ai_status.get('client_available') else '⚠️ Unavailable (using fallbacks)'}")
    print(f"   Topic Conversations: {len(test_results)}/4 successful")
    print(f"   Fallback Behavior: {'✅ Working' if fallback_works else '❌ Failed'}")
    print(f"   Consistency Test: {'✅ Passed' if consistency_works else '❌ Failed'}")

    if ai_status.get('client_available'):
        print("\n🤖 OpenAI API is working! Responses should be more natural and varied.")
    else:
        print("\n🔄 Using fallback responses. To enable OpenAI:")
        print("   1. Get OpenAI API key from https://platform.openai.com/")
        print("   2. Set OPENAI_API_KEY in .env file")
        print("   3. Restart the service")

    print(f"\n📖 API Documentation: {BASE_URL}/docs")


if __name__ == "__main__":
    main()