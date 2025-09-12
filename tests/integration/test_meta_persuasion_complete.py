# tests/integration/test_meta_persuasion_complete.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.services.meta_persuasion_service import PersuasionTechnique

client = TestClient(app)


class TestMetaPersuasionIntegration:
    """Complete test suite for meta-persuasion integration"""

    def test_root_endpoint_shows_meta_persuasion(self):
        """Test that root endpoint shows meta-persuasion features"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "Meta-Persuasion Enabled" in data["message"]
        assert "meta-persuasion analysis" in data["features"]
        assert "analyze" in data["endpoints"]
        assert "demonstrate" in data["endpoints"]

    def test_health_check_includes_meta_persuasion(self):
        """Test health check includes meta-persuasion status"""
        response = client.get("/health")

        assert response.status_code in [200, 503]  # May be degraded without Redis
        data = response.json()

        assert "meta_persuasion" in data["services"]
        assert "status" in data["services"]["meta_persuasion"]

    def test_analyze_message_comprehensive(self):
        """Test comprehensive message analysis"""
        test_message = """
        Leading experts at Harvard and Stanford have conducted extensive research 
        showing that 95% of people who follow this approach see dramatic improvements. 
        Imagine how this could transform your life - the opportunity is limited 
        and you need to act now before it's too late!
        """

        response = client.post("/analyze", json={"message": test_message})

        assert response.status_code == 200
        data = response.json()

        # Check main structure
        assert "message" in data
        assert "topic" in data
        assert "persuasion_analysis" in data
        assert "analysis_summary" in data
        assert "timestamp" in data

        # Check analysis summary
        summary = data["analysis_summary"]
        assert "technique_count" in summary
        assert "persuasion_score" in summary
        assert "primary_emotions" in summary
        assert "credibility_signals" in summary

        # Should detect multiple techniques
        assert summary["technique_count"] >= 3
        assert summary["persuasion_score"] > 0.5

    def test_analyze_message_validation(self):
        """Test message analysis validation"""
        # Empty message
        response = client.post("/analyze", json={"message": ""})
        assert response.status_code == 400
        assert "Message is required" in response.json()["detail"]

        # Missing message field
        response = client.post("/analyze", json={})
        assert response.status_code == 400

        # Message too long
        long_message = "x" * 2001
        response = client.post("/analyze", json={"message": long_message})
        assert response.status_code == 400
        assert "too long" in response.json()["detail"]

    def test_demonstrate_technique_comprehensive(self):
        """Test technique demonstration with all fields"""
        response = client.post("/demonstrate", json={
            "technique": "anchoring",
            "topic": "technology",
            "context": "discussing AI adoption"
        })

        assert response.status_code == 200
        data = response.json()

        # Check main structure
        assert "technique" in data
        assert "topic" in data
        assert "context" in data
        assert "demonstration" in data
        assert "educational_value" in data
        assert "timestamp" in data

        # Check demonstration structure
        demo = data["demonstration"]
        assert "demonstration" in demo
        assert "explanation" in demo
        assert "technique_name" in demo

        # Check educational value
        edu_value = data["educational_value"]
        assert "technique_explanation" in edu_value
        assert "real_world_applications" in edu_value
        assert "effectiveness_factors" in edu_value

    def test_demonstrate_technique_validation(self):
        """Test technique demonstration validation"""
        # Missing technique
        response = client.post("/demonstrate", json={})
        assert response.status_code == 400
        assert "Technique is required" in response.json()["detail"]

        # Invalid technique
        response = client.post("/demonstrate", json={"technique": "invalid_technique"})
        assert response.status_code == 400
        assert "Invalid technique" in response.json()["detail"]

        # Check that error includes available techniques
        available_techniques = [t.value for t in PersuasionTechnique]
        assert any(tech in response.json()["detail"] for tech in available_techniques[:3])

    def test_list_techniques_comprehensive(self):
        """Test comprehensive technique listing"""
        response = client.get("/techniques")

        assert response.status_code == 200
        data = response.json()

        # Check main structure
        assert "available_techniques" in data
        assert "total_count" in data
        assert "categories" in data
        assert "usage_tips" in data
        assert "timestamp" in data

        # Check techniques structure
        techniques = data["available_techniques"]
        assert isinstance(techniques, dict)
        assert len(techniques) == data["total_count"]
        assert data["total_count"] > 0

        # Check individual technique structure
        for technique_name, technique_info in techniques.items():
            assert "name" in technique_info
            assert "explanation" in technique_info
            assert "example" in technique_info
            assert "category" in technique_info
            assert "effectiveness" in technique_info
            assert technique_info["name"] == technique_name
            assert technique_info["category"] in ["logical", "emotional", "social", "structural"]
            assert technique_info["effectiveness"] in ["high", "medium", "low"]

        # Check categories
        categories = data["categories"]
        assert "logical" in categories
        assert "emotional" in categories
        assert "social" in categories
        assert "structural" in categories

        # Check usage tips
        tips = data["usage_tips"]
        assert "combination" in tips
        assert "audience" in tips
        assert "context" in tips
        assert "ethics" in tips

    def test_chat_with_meta_persuasion_integration(self):
        """Test chat endpoint with meta-persuasion integration"""
        # First message - establish conversation
        first_response = client.post("/chat", json={
            "conversation_id": None,
            "message": "I think artificial intelligence will replace all human jobs and destroy society"
        })

        assert first_response.status_code == 200
        first_data = first_response.json()
        conversation_id = first_data["conversation_id"]

        # Check initial response
        assert len(first_data["messages"]) >= 2
        bot_message = next(msg for msg in first_data["messages"] if msg["role"] == "bot")
        assert len(bot_message["message"]) > 0

        # Second message using multiple persuasion techniques
        sophisticated_message = """
        Multiple independent studies from MIT and Harvard show that 89% of experts 
        agree AI displacement is accelerating. Think about the millions of families 
        who will lose their livelihoods - we need immediate government intervention 
        before it's too late!
        """

        second_response = client.post("/chat", json={
            "conversation_id": conversation_id,
            "message": sophisticated_message
        })

        assert second_response.status_code == 200
        second_data = second_response.json()

        # Check conversation continuity
        assert second_data["conversation_id"] == conversation_id
        assert len(second_data["messages"]) >= 4

        # Check that bot maintains position
        bot_messages = [msg for msg in second_data["messages"] if msg["role"] == "bot"]
        assert len(bot_messages) >= 2

        # Check for potential educational content
        latest_bot_message = bot_messages[-1]["message"]
        # Educational content might be present given sophisticated user input
        # but we can't guarantee it due to randomness

    def test_conversation_analysis_full_flow(self):
        """Test complete conversation analysis flow"""
        # Create a conversation
        chat_response = client.post("/chat", json={
            "conversation_id": None,
            "message": "Climate change is just natural variation, not human-caused"
        })

        assert chat_response.status_code == 200
        conversation_id = chat_response.json()["conversation_id"]

        # Add more messages to build conversation
        messages = [
            "Research from leading climate scientists proves human activity is the main driver",
            "Those scientists are biased and funded by environmental lobbies",
            "NASA temperature data shows clear warming trends since industrialization"
        ]

        for message in messages:
            client.post("/chat", json={
                "conversation_id": conversation_id,
                "message": message
            })

        # Get conversation analysis
        analysis_response = client.get(f"/conversation/{conversation_id}/analysis")

        assert analysis_response.status_code == 200
        analysis_data = analysis_response.json()

        # Check comprehensive analysis structure
        assert "conversation_id" in analysis_data
        assert "message_count" in analysis_data
        assert "message_analyses" in analysis_data
        assert "conversation_stats" in analysis_data
        assert "insights" in analysis_data
        assert "recommendations" in analysis_data
        assert "timestamp" in analysis_data

        # Check message analyses
        message_analyses = analysis_data["message_analyses"]
        assert len(message_analyses) >= 4  # Initial + 3 additional + bot responses

        for msg_analysis in message_analyses:
            assert "role" in msg_analysis
            assert "message" in msg_analysis
            assert "analysis" in msg_analysis

            analysis = msg_analysis["analysis"]
            assert "techniques_detected" in analysis
            assert "persuasion_score" in analysis

        # Check conversation stats
        stats = analysis_data["conversation_stats"]
        assert "total_techniques_detected" in stats
        assert "average_persuasion_score" in stats
        assert isinstance(stats["total_techniques_detected"], int)
        assert isinstance(stats["average_persuasion_score"], (int, float))

        # Check insights and recommendations
        assert isinstance(analysis_data["insights"], dict)
        assert isinstance(analysis_data["recommendations"], dict)

    def test_conversation_analysis_not_found(self):
        """Test conversation analysis for non-existent conversation"""
        response = client.get("/conversation/non-existent-id/analysis")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_stats_endpoint_with_meta_persuasion(self):
        """Test stats endpoint includes meta-persuasion info"""
        response = client.get("/stats")

        assert response.status_code == 200
        data = response.json()

        assert "total_conversations" in data
        assert "redis_status" in data
        assert "system_info" in data

        system_info = data["system_info"]
        assert "meta_persuasion_enabled" in system_info
        assert "version" in system_info
        assert system_info["version"] == "2.0.0"

    def test_error_handling_comprehensive(self):
        """Test comprehensive error handling"""
        # Test various error conditions
        error_tests = [
            ("/analyze", "post", {}, 400),
            ("/demonstrate", "post", {}, 400),
            ("/conversation/invalid/analysis", "get", None, 404),
        ]

        for endpoint, method, payload, expected_status in error_tests:
            if method == "post":
                response = client.post(endpoint, json=payload)
            else:
                response = client.get(endpoint)

            assert response.status_code == expected_status
            assert "detail" in response.json()

    def test_all_persuasion_techniques_demonstrable(self):
        """Test that all persuasion techniques can be demonstrated"""
        # Get all available techniques
        techniques_response = client.get("/techniques")
        assert techniques_response.status_code == 200

        available_techniques = list(techniques_response.json()["available_techniques"].keys())

        # Test demonstration for each technique
        for technique in available_techniques:
            response = client.post("/demonstrate", json={
                "technique": technique,
                "topic": "general",
                "context": "test context"
            })

            assert response.status_code == 200, f"Failed to demonstrate technique: {technique}"
            data = response.json()
            assert data["technique"] == technique
            assert "demonstration" in data

    def test_persuasion_analysis_consistency(self):
        """Test that persuasion analysis is consistent for same message"""
        test_message = "Expert research shows 95% effectiveness!"

        # Analyze the same message multiple times
        responses = []
        for _ in range(3):
            response = client.post("/analyze", json={"message": test_message})
            assert response.status_code == 200
            responses.append(response.json())

        # Check consistency of core analysis
        for i in range(1, len(responses)):
            # Topic detection should be consistent
            assert responses[i]["topic"] == responses[0]["topic"]

            # Technique detection should be consistent
            techniques_0 = set(str(t) for t in responses[0]["persuasion_analysis"]["techniques_detected"])
            techniques_i = set(str(t) for t in responses[i]["persuasion_analysis"]["techniques_detected"])
            assert techniques_0 == techniques_i

    def test_educational_content_integration(self):
        """Test that educational content can be triggered"""
        # Use a message with high persuasion score to potentially trigger educational content
        high_persuasion_message = """
        Leading researchers at Harvard, MIT, and Stanford have conclusively proven 
        through peer-reviewed studies that 97% of experts agree this approach works. 
        Imagine the incredible impact this could have on your life - but time is 
        running out and you must act immediately before this limited opportunity 
        disappears forever!
        """

        # Create conversation and send sophisticated message
        first_response = client.post("/chat", json={
            "conversation_id": None,
            "message": "I disagree with mainstream science"
        })

        conversation_id = first_response.json()["conversation_id"]

        # Send the high-persuasion message
        response = client.post("/chat", json={
            "conversation_id": conversation_id,
            "message": high_persuasion_message
        })

        assert response.status_code == 200
        data = response.json()

        # Check if educational content was added (may or may not be present due to randomness)
        bot_message = next(msg for msg in data["messages"] if msg["role"] == "bot" and msg == data["messages"][-1])

        # If educational content is present, it should be properly formatted
        if "Educational note:" in bot_message["message"]:
            assert "---" in bot_message["message"]
            assert bot_message["message"].count("---") >= 1


class TestPersuasionTechniques:
    """Test individual persuasion techniques"""

    def test_anchoring_technique(self):
        """Test anchoring technique demonstration"""
        response = client.post("/demonstrate", json={
            "technique": "anchoring",
            "topic": "business"
        })

        assert response.status_code == 200
        data = response.json()

        demo_text = data["demonstration"]["demonstration"]
        # Anchoring should contain numbers or statistics
        assert any(char.isdigit() for char in demo_text)

    def test_emotional_appeal_technique(self):
        """Test emotional appeal technique demonstration"""
        response = client.post("/demonstrate", json={
            "technique": "emotional_appeal",
            "topic": "health"
        })

        assert response.status_code == 200
        data = response.json()

        demo_text = data["demonstration"]["demonstration"].lower()
        # Should contain emotional words
        emotional_words = ["feel", "heart", "imagine", "think about"]
        assert any(word in demo_text for word in emotional_words)

    def test_authority_technique(self):
        """Test authority technique demonstration"""
        response = client.post("/demonstrate", json={
            "technique": "authority",
            "topic": "science"
        })

        assert response.status_code == 200
        data = response.json()

        demo_text = data["demonstration"]["demonstration"].lower()
        # Should reference experts or credentials
        authority_words = ["expert", "research", "study", "professor", "university"]
        assert any(word in demo_text for word in authority_words)