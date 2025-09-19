#!/usr/bin/env python3
"""
Script de prueba para verificar que la lógica de oposición funciona correctamente
"""


def test_topic_extraction():
    """Test la lógica de extracción de temas y posiciones opuestas"""

    print("🧠 Testing Topic and Stance Extraction Logic")
    print("=" * 50)

    # Simulamos la lógica de extracción (copia del ai_service.py)
    import re

    def extract_topic_and_stance(first_message: str):
        """Copia de la función del ai_service.py para testing"""
        message_lower = first_message.lower().strip()

        patterns = [
            (r"(.+?)\s+is\s+better\s+than\s+(.+)", lambda m: (f"{m.group(1)} vs {m.group(2)}", m.group(2))),
            (r"why\s+(.+?)\s+is\s+better\s+than\s+(.+)", lambda m: (f"{m.group(1)} vs {m.group(2)}", m.group(2))),
            (r"explain\s+why\s+(.+?)\s+is\s+better\s+than\s+(.+)",
             lambda m: (f"{m.group(1)} vs {m.group(2)}", m.group(2))),
            (r"(.+?)\s+vs?\s+(.+)", lambda m: (f"{m.group(1)} vs {m.group(2)}", m.group(2))),
            (r"(.+?)\s+or\s+(.+)", lambda m: (f"{m.group(1)} or {m.group(2)}", m.group(2))),
        ]

        for pattern, extractor in patterns:
            match = re.search(pattern, message_lower)
            if match:
                topic, bot_stance = extractor(match)
                return topic.strip(), bot_stance.strip()

        controversial_topics = {
            "vaccine": "pro-vaccine safety and effectiveness",
            "climate": "climate action and environmental protection",
            "flat earth": "spherical Earth and scientific evidence",
            "android": "iPhone and iOS ecosystem",
            "ios": "Android and open-source advantages",
            "pc": "Mac and Apple ecosystem",
            "mac": "PC and Windows flexibility",
            "playstation": "Xbox and Microsoft gaming",
            "xbox": "PlayStation and Sony gaming",
            "coffee": "tea and its health benefits",
            "tea": "coffee and its energy benefits",
            "pepsi": "Coca-Cola and its superior taste",
            "coke": "Pepsi and its better flavor profile",
        }

        for keyword, stance in controversial_topics.items():
            if keyword in message_lower:
                return f"Discussion about {keyword}", stance

        return "General debate", f"the opposing viewpoint to: {first_message}"

    # Test cases
    test_cases = [
        # Caso específico del problema reportado
        {
            "input": "explain why pepsi is better than coke",
            "expected_bot_defends": "coke",
            "description": "Usuario defiende Pepsi → Bot debe defender Coke"
        },

        # Otros casos de prueba
        {
            "input": "android is better than ios",
            "expected_bot_defends": "ios",
            "description": "Usuario defiende Android → Bot debe defender iOS"
        },

        {
            "input": "playstation vs xbox",
            "expected_bot_defends": "xbox",
            "description": "Usuario menciona PS primero → Bot debe defender Xbox"
        },

        {
            "input": "why iphone is superior to android",
            "expected_bot_defends": "android",
            "description": "Usuario defiende iPhone → Bot debe defender Android"
        },

        {
            "input": "vaccines are dangerous",
            "expected_bot_defends": "vaccine",
            "description": "Usuario anti-vacunas → Bot debe defender vacunas"
        },

        {
            "input": "climate change is a hoax",
            "expected_bot_defends": "climate",
            "description": "Usuario niega clima → Bot debe defender acción climática"
        }
    ]

    results = []

    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {case['description']}")
        print(f"   Input: '{case['input']}'")

        topic, bot_stance = extract_topic_and_stance(case['input'])
        expected = case['expected_bot_defends'].lower()

        # Verificar si el bot defiende la posición esperada
        if expected in bot_stance.lower():
            print(f"   ✅ PASS: Bot will defend '{bot_stance}'")
            results.append("PASS")
        else:
            print(f"   ❌ FAIL: Bot will defend '{bot_stance}', expected to contain '{expected}'")
            results.append("FAIL")

    # Resumen
    passed = results.count("PASS")
    failed = results.count("FAIL")

    print(f"\n📊 RESULTS SUMMARY")
    print(f"   Passed: {passed}/{len(test_cases)}")
    print(f"   Failed: {failed}/{len(test_cases)}")

    if failed == 0:
        print("   🎉 ALL TESTS PASSED! Opposition logic working correctly.")
    else:
        print(f"   ⚠️  {failed} tests failed. Opposition logic needs adjustment.")

    return failed == 0


def test_fallback_responses():
    """Test las respuestas fallback de oposición"""

    print("\n🔄 Testing Fallback Opposition Responses")
    print("=" * 50)

    # Simulamos las respuestas fallback
    fallback_responses = {
        "pepsi": "I understand you prefer Pepsi, but Coca-Cola is actually superior! The classic formula has been perfected for over 130 years, creating that perfect balance of sweetness and refreshment that Pepsi simply can't match.",
        "android": "While Android has its merits, iPhone's iOS ecosystem is genuinely superior. The seamless integration, consistent updates, and premium app experience create a user experience that Android fragmentation simply can't deliver.",
        "playstation": "PlayStation has its fans, but Xbox delivers superior value and performance. Game Pass alone offers incredible value, plus the backwards compatibility and power of Series X make it the better gaming investment."
    }

    test_messages = [
        "explain why pepsi is better than coke",
        "android is better than ios",
        "playstation beats xbox"
    ]

    print("Testing fallback responses for opposition:")

    for message in test_messages:
        print(f"\nInput: '{message}'")

        # Check which fallback would be used
        message_lower = message.lower()
        fallback_used = None

        for key, response in fallback_responses.items():
            if key in message_lower:
                fallback_used = response
                break

        if fallback_used:
            # Check if the response actually defends the opposite position
            if "pepsi" in message_lower and "coca-cola" in fallback_used.lower():
                print("   ✅ PASS: Defends Coke against Pepsi")
            elif "android" in message_lower and "iphone" in fallback_used.lower():
                print("   ✅ PASS: Defends iPhone against Android")
            elif "playstation" in message_lower and "xbox" in fallback_used.lower():
                print("   ✅ PASS: Defends Xbox against PlayStation")
            else:
                print("   ❌ FAIL: Fallback doesn't clearly defend opposite position")
        else:
            print("   ⚠️  WARNING: No specific fallback found, would use generic response")


def test_api_integration():
    """Test de integración con la API real"""

    print("\n🌐 Testing API Integration (if server is running)")
    print("=" * 50)

    try:
        import requests
        import json

        base_url = "http://localhost:8000"

        # Test básico de conexión
        try:
            health_response = requests.get(f"{base_url}/health", timeout=5)
            if health_response.status_code != 200:
                print("❌ Server not responding to health check")
                return False
        except requests.exceptions.RequestException:
            print("⚠️  Server not running. Start with: make run")
            return False

        # Test del caso específico: pepsi vs coke
        print("\n🧪 Testing the specific reported case: Pepsi vs Coke")

        payload = {
            "conversation_id": None,
            "message": "explain why pepsi is better than coke"
        }

        response = requests.post(
            f"{base_url}/chat",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            bot_message = data["messages"][-1]["message"].lower()

            print(f"✅ API Response received")
            print(f"Bot said: {data['messages'][-1]['message'][:150]}...")

            # Verificar que el bot defiende Coke
            if "coke" in bot_message or "coca-cola" in bot_message:
                if not ("pepsi is better" in bot_message or "you're right about pepsi" in bot_message):
                    print("✅ PASS: Bot correctly defends Coke against Pepsi!")
                    return True
                else:
                    print("❌ FAIL: Bot agrees with user instead of defending Coke")
                    return False
            else:
                print("❌ FAIL: Bot doesn't mention Coke in defense")
                return False
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return False

    except ImportError:
        print("⚠️  requests library not available. Install with: pip install requests")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False


def main():
    """Función principal que ejecuta todas las pruebas"""

    print("🔍 OPPOSITION LOGIC VALIDATION TEST")
    print("=" * 60)
    print("This script validates that the bot correctly takes opposing stances")
    print("=" * 60)

    # Test 1: Topic extraction logic
    extraction_passed = test_topic_extraction()

    # Test 2: Fallback responses
    test_fallback_responses()

    # Test 3: API integration (if available)
    api_passed = test_api_integration()

    # Final summary
    print("\n" + "=" * 60)
    print("📋 FINAL SUMMARY")
    print("=" * 60)

    if extraction_passed:
        print("✅ Topic Extraction Logic: WORKING")
    else:
        print("❌ Topic Extraction Logic: NEEDS FIX")

    if api_passed:
        print("✅ API Integration: WORKING")
        print("🎉 The opposition logic is working correctly!")
        print("   Bot will now defend opposite positions as required.")
    elif api_passed is False:
        print("❌ API Integration: ISSUES DETECTED")
        print("⚠️  The bot may not be defending opposite positions correctly.")
    else:
        print("⚠️  API Integration: NOT TESTED (server not running)")

    print("\n💡 TO FIX THE REPORTED ISSUE:")
    print("   1. Ensure the updated ai_service.py is deployed")
    print("   2. Restart the server: make down && make run")
    print("   3. Test with: 'explain why pepsi is better than coke'")
    print("   4. Bot should defend Coke, not agree with Pepsi")


if __name__ == "__main__":
    main()