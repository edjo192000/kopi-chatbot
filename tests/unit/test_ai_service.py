# tests/unit/test_ai_service.py
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.ai_service import AIService
from app.models.chat_models import Message
from app.config import settings


class TestAIService:
    """Test suite for AI Service"""

    def setup_method(self):
        """Setup for each test"""
        # Reset settings for testing
        self.original_api_key = settings.openai_api_key
        self.original_enabled = settings.openai_enabled

    def teardown_method(self):
        """Cleanup after each test"""
        settings.openai_api_key = self.original_api_key
        settings.openai_enabled = self.original_enabled

    def test_ai_service_initialization_no_key(self):
        """Test AI service initialization without API key"""
        settings.openai_api_key = None
        ai_service = AIService()

        assert ai_service.client is None
        assert ai_service.is_available is False

    def test_ai_service_initialization_disabled(self):
        """Test AI service initialization when disabled"""
        settings.openai_api_key = "test-key"
        settings.openai_enabled = False
        ai_service = AIService()

        assert ai_service.client is None
        assert ai_service.is_available is False

    @patch('app.services.ai_service.OpenAI')
    def test_ai_service_initialization_success(self, mock_openai):
        """Test successful AI service initialization"""
        settings.openai_api_key = "test-key"
        settings.openai_enabled = True

        # Mock successful client creation
        mock_client = Mock()
        mock_client.models.list.return_value = []
        mock_openai.return_value = mock_client

        ai_service = AIService()

        assert ai_service.client is not None
        assert ai_service.is_available is True
        mock_openai.assert_called_once()

    @patch('app.services.ai_service.OpenAI')
    def test_ai_service_initialization_failure(self, mock_openai):
        """Test AI service initialization failure"""
        settings.openai_api_key = "test-key"
        settings.openai_enabled = True

        # Mock client creation failure
        mock_openai.side_effect = Exception("API Error")

        ai_service = AIService()

        assert ai_service.client is None
        assert ai_service.is_available is False

    def test_detect_topic_flat_earth(self):
        """Test topic detection for flat earth"""
        ai_service = AIService()

        test_cases = [
            "I think the Earth is flat",
            "The globe model is wrong",
            "NASA lies about the curved horizon",
            "The Earth is a sphere but I disagree"
        ]

        for message in test_cases:
            topic = ai_service.detect_topic(message)
            assert topic == "flat_earth"

    def test_detect_topic_vaccines(self):
        """Test topic detection for vaccines"""
        ai_service = AIService()

        test_cases = [
            "Vaccines are dangerous",
            "I got my COVID vaccination today",
            "Pfizer vaccine side effects",
            "Immunization schedule for children"
        ]

        for message in test_cases:
            topic = ai_service.detect_topic(message)
            assert topic == "vaccines"

    def test_detect_topic_climate(self):
        """Test topic detection for climate"""
        ai_service = AIService()

        test_cases = [
            "Climate change is real",
            "Global warming is fake",
            "Carbon emissions are destroying the environment",
            "Greenhouse gases cause temperature rise"
        ]

        for message in test_cases:
            topic = ai_service.detect_topic(message)
            assert topic == "climate"

    def test_detect_topic_crypto(self):
        """Test topic detection for crypto"""
        ai_service = AIService()

        test_cases = [
            "Bitcoin is the future",
            "Cryptocurrency is a scam",
            "Blockchain technology is revolutionary",
            "Ethereum price prediction"
        ]

        for message in test_cases:
            topic = ai_service.detect_topic(message)
            assert topic == "crypto"

    def test_detect_topic_general(self):
        """Test topic detection for general topics"""
        ai_service = AIService()

        test_cases = [
            "Hello there",
            "What's the weather like?",
            "I love pizza",
            "Tell me about quantum physics"
        ]

        for message in test_cases:
            topic = ai_service.detect_topic(message)
            assert topic == "general"

    @pytest.mark.asyncio
    async def test_generate_response_unavailable(self):
        """Test generate_response when AI is unavailable"""
        ai_service = AIService()
        ai_service.is_available = False

        messages = [Message(role="user", message="Test message")]
        response = await ai_service.generate_response(messages, "general")

        assert response is None

    @pytest.mark.asyncio
    @patch('app.services.ai_service.AIService._generate_position_response')
    async def test_generate_response_first_message(self, mock_position):
        """Test generate_response for first message"""
        mock_position.return_value = "Test position response"

        ai_service = AIService()
        ai_service.is_available = True
        ai_service.client = Mock()

        messages = [Message(role="user", message="Test message")]
        response = await ai_service.generate_response(messages, "general")

        mock_position.assert_called_once_with(messages[0], "general")
        assert response == "Test position response"

    @pytest.mark.asyncio
    @patch('app.services.ai_service.AIService._generate_debate_response')
    async def test_generate_response_continuing_conversation(self, mock_debate):
        """Test generate_response for continuing conversation"""
        mock_debate.return_value = "Test debate response"

        ai_service = AIService()
        ai_service.is_available = True
        ai_service.client = Mock()

        messages = [
            Message(role="user", message="First message"),
            Message(role="bot", message="Bot response"),
            Message(role="user", message="Second message")
        ]
        response = await ai_service.generate_response(messages, "general")

        mock_debate.assert_called_once_with(messages, "general")
        assert response == "Test debate response"

    @pytest.mark.asyncio
    @patch('app.services.ai_service.AIService._call_openai')
    async def test_generate_position_response(self, mock_call):
        """Test generate_position_response"""
        mock_call.return_value = "Test AI position"

        ai_service = AIService()
        ai_service.is_available = True
        ai_service.client = Mock()

        user_message = Message(role="user", message="I think vaccines are bad")
        response = await ai_service._generate_position_response(user_message, "vaccines")

        mock_call.assert_called_once()
        assert response == "Test AI position"

    @pytest.mark.asyncio
    @patch('app.services.ai_service.AIService._call_openai')
    async def test_generate_debate_response(self, mock_call):
        """Test generate_debate_response"""
        mock_call.return_value = "Test AI debate"

        ai_service = AIService()
        ai_service.is_available = True
        ai_service.client = Mock()

        messages = [
            Message(role="user", message="First message"),
            Message(role="bot", message="Bot position"),
            Message(role="user", message="Counter argument")
        ]
        response = await ai_service._generate_debate_response(messages, "vaccines")

        mock_call.assert_called_once()
        assert response == "Test AI debate"

    @pytest.mark.asyncio
    async def test_call_openai_success(self):
        """Test successful OpenAI API call"""
        ai_service = AIService()
        ai_service.is_available = True

        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test AI response"
        mock_client.chat.completions.create.return_value = mock_response
        ai_service.client = mock_client

        response = await ai_service._call_openai("System prompt", "User prompt")

        assert response == "Test AI response"
        mock_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_call_openai_failure(self):
        """Test failed OpenAI API call"""
        ai_service = AIService()
        ai_service.is_available = True

        # Mock OpenAI client with failure
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        ai_service.client = mock_client

        response = await ai_service._call_openai("System prompt", "User prompt")

        assert response is None

    def test_get_status(self):
        """Test get_status method"""
        ai_service = AIService()
        ai_service.is_available = True

        status = ai_service.get_status()

        assert "openai_enabled" in status
        assert "api_key_configured" in status
        assert "client_available" in status
        assert "model" in status
        assert "max_tokens" in status
        assert "temperature" in status

        assert status["client_available"] is True