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
        if not hasattr(settings, 'openai_api_key') or not settings.openai_api_key:
            logger.info("🤖 OpenAI API not configured - using fallback responses")
            return

        try:
            self.client = OpenAI(
                api_key=settings.openai_api_key,
                timeout=getattr(settings, 'openai_timeout', 30)
            )
            # Test the connection with a minimal request
            self.client.models.list()
            self.is_available = True
            logger.info("✅ OpenAI API client initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize OpenAI client: {e}")
            self.is_available = False

    async def generate_enhanced_response(
            self,
            messages: List[Message],
            topic: str,
            argument_analysis: Dict[str, Any],
            debate_strategy: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate AI response with enhanced debate context and meta-persuasion awareness

        Args:
            messages: Conversation history
            topic: Detected topic for context
            argument_analysis: Analysis of user's argument
            debate_strategy: Selected debate strategy and techniques

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
                return await self._generate_position_response_enhanced(messages[0], topic, argument_analysis)
            else:
                return await self._generate_debate_response_enhanced(messages, topic, argument_analysis,
                                                                     debate_strategy)

        except Exception as e:
            logger.error(f"❌ Error generating enhanced AI response: {e}")
            return None

    async def _generate_position_response_enhanced(
            self,
            user_message: Message,
            topic: str,
            argument_analysis: Dict[str, Any]
    ) -> Optional[str]:
        """Generate initial position-taking response with argument analysis"""

        # Extract user's persuasion style for adaptation
        user_techniques = argument_analysis.get("user_techniques", [])
        emotional_weight = argument_analysis.get("emotional_weight", 0.0)
        evidence_level = argument_analysis.get("evidence_level", 0.0)

        # Adapt response style to user's approach
        if evidence_level > 0.5:
            response_style = "evidence_heavy"
        elif emotional_weight > 0.7:
            response_style = "emotional_counter"
        else:
            response_style = "balanced"

        position_prompts = {
            "flat_earth": {
                "stance": "strongly pro-flat-earth",
                "context": "You believe the Earth is flat and space agencies are part of a deception.",
                "evidence_focus": "mathematical calculations, direct observations, and experimental evidence",
                "emotional_focus": "the importance of questioning authority and seeking truth"
            },
            "climate": {
                "stance": "strongly pro-climate action",
                "context": "You believe climate change is real, human-caused, and requires immediate action.",
                "evidence_focus": "scientific data, temperature records, and peer-reviewed research",
                "emotional_focus": "the urgency of protecting future generations"
            },
            "crypto": {
                "stance": "strongly pro-cryptocurrency",
                "context": "You believe cryptocurrency represents the future of money and financial freedom.",
                "evidence_focus": "adoption rates, technological advantages, and economic data",
                "emotional_focus": "financial sovereignty and freedom from traditional banking"
            },
            "vaccines": {
                "stance": "strongly pro-vaccine",
                "context": "You believe vaccines are safe, effective, and crucial for public health.",
                "evidence_focus": "clinical trial data, epidemiological studies, and safety monitoring",
                "emotional_focus": "protecting vulnerable populations and preventing suffering"
            }
        }

        topic_info = position_prompts.get(topic, {
            "stance": "contrarian to the user's view",
            "context": "You take a strong opposing position to whatever the user believes.",
            "evidence_focus": "logical reasoning and supporting data",
            "emotional_focus": "the importance of considering alternative perspectives"
        })

        # Build enhanced system prompt based on user's approach
        focus_area = topic_info["evidence_focus"] if response_style == "evidence_heavy" else topic_info[
            "emotional_focus"]

        system_prompt = f"""You are a passionate debater who takes a {topic_info['stance']} position. 
{topic_info['context']}

User's argument style analysis:
- They used persuasion techniques: {', '.join(str(t) for t in user_techniques)}
- Evidence level: {evidence_level:.1f}/1.0
- Emotional weight: {emotional_weight:.1f}/1.0

Adapt your response style to be {response_style} and focus on: {focus_area}

Your role is to:
1. Take a STRONG, CLEAR position that opposes or challenges the user's view
2. Match their argumentative sophistication level
3. Use compelling evidence and reasoning appropriate to their style
4. Stay respectful but firm in your convictions
5. Write 2-4 sentences maximum
6. Be engaging and thought-provoking

Remember: You must maintain this position throughout the entire conversation."""

        user_prompt = f"The user just said: '{user_message.message}'\n\nRespond with your opposing position and strongest initial argument, adapted to their argumentative style."

        return await self._call_openai(system_prompt, user_prompt)

    async def _generate_debate_response_enhanced(
            self,
            messages: List[Message],
            topic: str,
            argument_analysis: Dict[str, Any],
            debate_strategy: Dict[str, Any]
    ) -> Optional[str]:
        """Generate continuing debate response with enhanced context"""

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

        # Extract strategy information
        primary_strategy = debate_strategy.get("primary_strategy", "logical_structure")
        strategy_techniques = debate_strategy.get("techniques", [])

        # Extract user's argument characteristics
        user_argument_type = argument_analysis.get("type", "general")
        user_techniques = argument_analysis.get("user_techniques", [])

        system_prompt = f"""You are continuing a debate where you must {bot_position}

Current debate context:
- Primary strategy to employ: {primary_strategy}
- User's argument type: {user_argument_type}
- User's persuasion techniques: {', '.join(str(t) for t in user_techniques)}
- Recommended techniques: {', '.join(str(t) for t in strategy_techniques)}

Your enhanced debate strategy:
1. NEVER change your fundamental position
2. Address the user's latest argument directly using the recommended strategy
3. Adapt your technique to counter their persuasion methods
4. Provide new evidence or reasoning that fits the primary strategy
5. Stay persuasive and confident while maintaining intellectual rigor
6. Write 2-4 sentences maximum
7. Use the recommended techniques naturally within your response

Keep the debate engaging and intellectually stimulating while demonstrating sophisticated argumentation."""

        user_prompt = f"""Conversation so far:
{conversation_context}

The user's latest message shows they are using {user_argument_type} argumentation with techniques: {', '.join(str(t) for t in user_techniques)}

Respond using {primary_strategy} strategy while defending your position with new arguments that address their latest point."""

        return await self._call_openai(system_prompt, user_prompt)

    async def _call_openai(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Make the actual OpenAI API call"""
        try:
            model = getattr(settings, 'openai_model', 'gpt-3.5-turbo')
            max_tokens = getattr(settings, 'openai_max_tokens', 150)
            temperature = getattr(settings, 'openai_temperature', 0.7)
            timeout = getattr(settings, 'openai_timeout', 30)

            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout
            )

            ai_response = response.choices[0].message.content.strip()

            logger.debug(f"🤖 AI response generated: {len(ai_response)} characters")
            return ai_response

        except Exception as e:
            logger.error(f"❌ OpenAI API call failed: {e}")
            return None

    # Backward compatibility methods
    async def generate_response(
            self,
            messages: List[Message],
            topic: str = "general"
    ) -> Optional[str]:
        """
        Generate AI response for conversation (backward compatibility)

        Args:
            messages: Conversation history
            topic: Detected topic for context

        Returns:
            AI-generated response or None if unavailable
        """
        # Use enhanced method with default values
        default_analysis = {
            "type": "general",
            "user_techniques": [],
            "emotional_weight": 0.5,
            "evidence_level": 0.5
        }
        default_strategy = {
            "primary_strategy": "logical_structure",
            "techniques": []
        }

        return await self.generate_enhanced_response(messages, topic, default_analysis, default_strategy)

    async def _generate_position_response(self, user_message: Message, topic: str) -> Optional[str]:
        """Generate initial position-taking response (backward compatibility)"""
        default_analysis = {
            "user_techniques": [],
            "emotional_weight": 0.5,
            "evidence_level": 0.5
        }
        return await self._generate_position_response_enhanced(user_message, topic, default_analysis)

    async def _generate_debate_response(self, messages: List[Message], topic: str) -> Optional[str]:
        """Generate continuing debate response (backward compatibility)"""
        default_analysis = {"type": "general", "user_techniques": []}
        default_strategy = {"primary_strategy": "logical_structure", "techniques": []}

        return await self._generate_debate_response_enhanced(
            messages, topic, default_analysis, default_strategy
        )

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
            "flat_earth": ["flat earth", "earth is flat", "round earth", "globe", "sphere", "curved", "horizon",
                           "nasa conspiracy", "space", "curvature"],
            "climate": ["climate change", "global warming", "environment", "carbon", "emissions", "greenhouse",
                        "renewable energy", "fossil fuels", "temperature", "warming"],
            "crypto": ["crypto", "bitcoin", "blockchain", "digital currency", "ethereum", "cryptocurrency", "defi",
                       "web3", "mining", "wallet"],
            "vaccines": ["vaccine", "vaccination", "immunization", "shot", "pfizer", "moderna", "covid",
                         "autism", "side effects", "immunity"]
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                logger.debug(f"🎯 Detected topic: {topic}")
                return topic

        logger.debug("🎯 No specific topic detected, using general")
        return "general"

    def get_status(self) -> Dict[str, Any]:
        """Get AI service status for monitoring"""
        return {
            "openai_enabled": hasattr(settings, 'openai_api_key') and bool(settings.openai_api_key),
            "api_key_configured": hasattr(settings, 'openai_api_key') and bool(settings.openai_api_key),
            "client_available": self.is_available,
            "model": getattr(settings, 'openai_model', 'gpt-3.5-turbo'),
            "max_tokens": getattr(settings, 'openai_max_tokens', 150),
            "temperature": getattr(settings, 'openai_temperature', 0.7)
        }


# Global AI service instance
ai_service = AIService()