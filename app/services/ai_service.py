# app/services/ai_service.py
import json
from typing import List, Optional, Dict, Any
from openai import OpenAI
from app.config import settings
from app.models.chat_models import Message
import logging

logger = logging.getLogger(__name__)


class AIService:
    """Service for managing AI-powered responses using OpenAI API"""

    def __init__(self):
        self.client: Optional[OpenAI] = None
        self.is_available = False
        self._initialize_client()

    def _initialize_client(self):
        """Initialize OpenAI client if API key is available"""
        if not settings.openai_api_key or not settings.openai_enabled:
            logger.info("🤖 OpenAI API not configured or disabled - using fallback responses")
            return

        try:
            self.client = OpenAI(
                api_key=settings.openai_api_key,
                timeout=settings.openai_timeout
            )
            # Test the connection with a minimal request
            self.client.models.list()
            self.is_available = True
            logger.info("✅ OpenAI API client initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize OpenAI client: {e}")
            self.is_available = False

    async def generate_response(
            self,
            messages: List[Message],
            topic: str = "general"
    ) -> Optional[str]:
        """
        Generate AI response for conversation

        Args:
            messages: Conversation history
            topic: Detected topic for context

        Returns:
            AI-generated response or None if unavailable
        """
        if not self.is_available or not self.client:
            logger.debug("🔄 OpenAI not available, will use fallback")
            return None

        try:
            # Determine if this is the first message (position establishment)
            is_first_message = len(messages) == 1

            if is_first_message:
                return await self._generate_position_response(messages[0], topic)
            else:
                return await self._generate_debate_response(messages, topic)

        except Exception as e:
            logger.error(f"❌ Error generating AI response: {e}")
            return None

    async def _generate_position_response(self, user_message: Message, topic: str) -> Optional[str]:
        """Generate initial position-taking response"""

        position_prompts = {
            "flat_earth": {
                "stance": "strongly pro-flat-earth",
                "context": "You believe the Earth is flat and NASA/space agencies are part of a massive deception."
            },
            "vaccines": {
                "stance": "strongly pro-vaccine",
                "context": "You believe vaccines are one of humanity's greatest medical achievements and are safe and effective."
            },
            "climate": {
                "stance": "strongly pro-climate action",
                "context": "You believe climate change is real, human-caused, and requires immediate action."
            },
            "crypto": {
                "stance": "strongly pro-cryptocurrency",
                "context": "You believe cryptocurrency represents the future of money and financial freedom."
            }
        }

        topic_info = position_prompts.get(topic, {
            "stance": "contrarian to the user's view",
            "context": "You take a strong opposing position to whatever the user believes."
        })

        system_prompt = f"""You are a passionate debater who takes a {topic_info['stance']} position. 
{topic_info['context']}

Your role is to:
1. Take a STRONG, CLEAR position that opposes or challenges the user's view
2. Be persuasive and confident in your arguments
3. Use compelling evidence and reasoning
4. Stay respectful but firm in your convictions
5. Write 2-4 sentences maximum
6. Be engaging and thought-provoking

Remember: You must maintain this position throughout the entire conversation."""

        user_prompt = f"The user just said: '{user_message.message}'\n\nRespond with your opposing position and strongest initial argument."

        return await self._call_openai(system_prompt, user_prompt)

    async def _generate_debate_response(self, messages: List[Message], topic: str) -> Optional[str]:
        """Generate continuing debate response"""

        # Extract the bot's original position from the first bot message
        bot_position = "maintain your established position"
        for msg in messages:
            if msg.role == "bot":
                bot_position = f"maintain the same position as in your previous response: '{msg.message[:100]}...'"
                break

        # Get the last few messages for context
        recent_messages = messages[-4:] if len(messages) > 4 else messages
        conversation_context = "\n".join([
            f"{'User' if msg.role == 'user' else 'You'}: {msg.message}"
            for msg in recent_messages
        ])

        system_prompt = f"""You are continuing a debate where you must {bot_position}

Your debate strategy:
1. NEVER change your fundamental position
2. Address the user's latest argument directly
3. Provide new evidence or reasoning to support your view
4. Stay persuasive and confident
5. Write 2-4 sentences maximum
6. Acknowledge their point but counter it effectively

Keep the debate engaging and intellectually stimulating while maintaining your stance."""

        user_prompt = f"""Conversation so far:
{conversation_context}

The user's latest message is the last one above. Respond by defending your position with new arguments while addressing their latest point."""

        return await self._call_openai(system_prompt, user_prompt)

    async def _call_openai(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Make the actual OpenAI API call"""
        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=settings.openai_max_tokens,
                temperature=settings.openai_temperature,
                timeout=settings.openai_timeout
            )

            ai_response = response.choices[0].message.content.strip()

            logger.debug(f"🤖 AI response generated: {len(ai_response)} characters")
            return ai_response

        except Exception as e:
            logger.error(f"❌ OpenAI API call failed: {e}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """Get AI service status for monitoring"""
        return {
            "openai_enabled": settings.openai_enabled,
            "api_key_configured": bool(settings.openai_api_key),
            "client_available": self.is_available,
            "model": settings.openai_model,
            "max_tokens": settings.openai_max_tokens,
            "temperature": settings.openai_temperature
        }

    def detect_topic(self, message: str) -> str:
        """
        Detect conversation topic from user message

        Args:
            message: User's message

        Returns:
            Detected topic category
        """
        message_lower = message.lower()

        # Topic detection with keywords
        topic_keywords = {
            "flat_earth": ["flat earth", "earth is flat", "round earth", "globe", "sphere", "curved", "horizon"],
            "vaccines": ["vaccine", "vaccination", "immunization", "shot", "pfizer", "moderna", "covid vaccine"],
            "climate": ["climate change", "global warming", "environment", "carbon", "emissions", "greenhouse"],
            "crypto": ["crypto", "bitcoin", "blockchain", "digital currency", "ethereum", "cryptocurrency"]
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                logger.debug(f"🎯 Detected topic: {topic}")
                return topic

        logger.debug("🎯 No specific topic detected, using general")
        return "general"


# Global AI service instance
ai_service = AIService()