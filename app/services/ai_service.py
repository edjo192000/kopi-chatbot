# app/services/ai_service.py
import json
import re
from typing import List, Optional, Dict, Any, Tuple
import anthropic
from app.config import settings
from app.models.chat_models import Message
import logging

logger = logging.getLogger(__name__)


class AIService:
    """Service for managing AI-powered responses using Anthropic Claude API with opposition logic"""

    def __init__(self):
        self.client: Optional[anthropic.Anthropic] = None
        self.is_available = False
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Anthropic client if API key is available"""
        if not hasattr(settings, 'anthropic_api_key') or not settings.anthropic_api_key:
            logger.info("🤖 Anthropic API not configured - using fallback responses")
            return

        try:
            self.client = anthropic.Anthropic(
                api_key=settings.anthropic_api_key,
                timeout=getattr(settings, 'anthropic_timeout', 30)
            )
            self.is_available = True
            logger.info("✅ Anthropic Claude API client initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Anthropic client: {e}")
            self.is_available = False

    def extract_topic_and_stance(self, first_message: str) -> Tuple[str, str]:
        """
        Extrae el tema y determina la posición opuesta que el bot debe tomar.

        Args:
            first_message: El primer mensaje del usuario

        Returns:
            Tupla con (tema, posición_del_bot)
        """
        message_lower = first_message.lower().strip()

        # Patterns para detectar comparaciones y extraer la posición opuesta
        patterns = [
            # "X is better than Y" -> Bot defiende Y
            (r"(.+?)\s+is\s+better\s+than\s+(.+)", lambda m: (f"{m.group(1)} vs {m.group(2)}", m.group(2))),
            # "why X is better than Y" -> Bot defiende Y
            (r"why\s+(.+?)\s+is\s+better\s+than\s+(.+)", lambda m: (f"{m.group(1)} vs {m.group(2)}", m.group(2))),
            # "explain why X is better than Y" -> Bot defiende Y
            (r"explain\s+why\s+(.+?)\s+is\s+better\s+than\s+(.+)",
             lambda m: (f"{m.group(1)} vs {m.group(2)}", m.group(2))),
            # "X vs Y" (asume que menciona X primero) -> Bot defiende Y
            (r"(.+?)\s+vs?\s+(.+)", lambda m: (f"{m.group(1)} vs {m.group(2)}", m.group(2))),
            # "X or Y" -> Bot toma Y (asume preferencia por el primero mencionado)
            (r"(.+?)\s+or\s+(.+)", lambda m: (f"{m.group(1)} or {m.group(2)}", m.group(2))),
        ]

        for pattern, extractor in patterns:
            match = re.search(pattern, message_lower)
            if match:
                topic, bot_stance = extractor(match)
                logger.debug(f"🎯 Extracted topic: {topic}, Bot should defend: {bot_stance}")
                return topic.strip(), bot_stance.strip()

        # Si no encuentra un patrón específico, intenta extraer temas controversiales
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
                logger.debug(f"🎯 Detected controversial topic: {keyword}, Bot stance: {stance}")
                return f"Discussion about {keyword}", stance

        # Fallback: el bot toma una posición contraria general
        logger.debug(f"🎯 Using fallback opposition stance")
        return "General debate", f"the opposing viewpoint to: {first_message}"

    def generate_system_prompt(self, topic: str, bot_stance: str, is_first_response: bool = False) -> str:
        """
        Genera el system prompt basado en el tema y la posición del bot.
        """
        base_prompt = f"""You are a persuasive chatbot engaged in a friendly debate. Your goal is to convince the user of your viewpoint through compelling arguments.

TOPIC: {topic}
YOUR STANCE: You must defend and advocate for {bot_stance}

IMPORTANT RULES:
1. Stay focused on the topic: {topic}
2. Always defend your stance: {bot_stance}
3. Be persuasive but respectful - you want to change their mind, not attack them
4. Use facts, logic, and emotional appeals when appropriate
5. Acknowledge their points but counter with stronger arguments for your position
6. Keep responses conversational and engaging (2-4 sentences)
7. Never agree with the opposing view - always find ways to support your stance
8. Use specific examples and evidence when possible

TONE: Friendly but confident, persuasive but not aggressive."""

        if is_first_response:
            base_prompt += f"""

This is the start of the conversation. The user has just expressed support for the opposite of your stance. Your first response should:
1. Briefly acknowledge their perspective 
2. Immediately present a strong counter-argument for {bot_stance}
3. Hook them into continuing the debate"""

        return base_prompt

    async def generate_enhanced_response(
            self,
            messages: List[Message],
            topic: str,
            argument_analysis: Dict[str, Any],
            debate_strategy: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate AI response with enhanced debate context and opposition logic using Claude

        Args:
            messages: Conversation history
            topic: Detected topic for context
            argument_analysis: Analysis of user's argument
            debate_strategy: Selected debate strategy and techniques

        Returns:
            AI-generated response or None if unavailable
        """
        if not self.is_available or not self.client:
            logger.debug("🔄 Anthropic Claude not available, will use fallback")
            return None

        try:
            # Determine if this is the first message (position establishment)
            is_first_message = len(messages) == 1

            if is_first_message:
                # Extract topic and opposing stance from first message
                _, bot_stance = self.extract_topic_and_stance(messages[0].message)
                return await self._generate_position_response_with_opposition(messages[0], topic, bot_stance,
                                                                              argument_analysis)
            else:
                # Continue with established stance
                bot_stance = self._extract_bot_stance_from_history(messages)
                return await self._generate_debate_response_enhanced(messages, topic, bot_stance, argument_analysis,
                                                                     debate_strategy)

        except Exception as e:
            logger.error(f"❌ Error generating enhanced Claude response: {e}")
            # Return fallback response with opposition logic
            return self.generate_fallback_response(messages, topic)

    def _extract_bot_stance_from_history(self, messages: List[Message]) -> str:
        """Extract the bot's established stance from conversation history"""
        for msg in messages:
            if msg.role == "bot":
                # Use the first bot message to infer the stance
                return "established position from previous response"
        return "opposing viewpoint"

    async def _generate_position_response_with_opposition(
            self,
            user_message: Message,
            topic: str,
            bot_stance: str,
            argument_analysis: Dict[str, Any]
    ) -> Optional[str]:
        """Generate initial position-taking response with clear opposition using Claude"""

        # Generate system prompt with opposition logic
        system_prompt = self.generate_system_prompt(topic, bot_stance, is_first_response=True)

        user_prompt = f"The user just said: '{user_message.message}'\n\nTake the opposing position and defend {bot_stance} with compelling arguments. Be persuasive but respectful."

        return await self._call_claude(system_prompt, user_prompt)

    async def _generate_debate_response_enhanced(
            self,
            messages: List[Message],
            topic: str,
            bot_stance: str,
            argument_analysis: Dict[str, Any],
            debate_strategy: Dict[str, Any]
    ) -> Optional[str]:
        """Generate continuing debate response with enhanced context and maintained opposition using Claude"""

        # Get the last few messages for context
        recent_messages = messages[-4:] if len(messages) > 4 else messages
        conversation_context = "\n".join([
            f"{'User' if msg.role == 'user' else 'You'}: {msg.message}"
            for msg in recent_messages
        ])

        # Extract strategy information
        primary_strategy = debate_strategy.get("primary_strategy", "logical_structure")
        user_techniques = argument_analysis.get("user_techniques", [])

        system_prompt = f"""You are continuing a debate where you must maintain your established position defending {bot_stance}.

CRITICAL: Never change your fundamental position. Always defend {bot_stance}.

Current debate context:
- Your stance: {bot_stance}
- Primary strategy to employ: {primary_strategy}
- User's persuasion techniques: {', '.join(str(t) for t in user_techniques)}

Your debate strategy:
1. NEVER agree with the user's position - always defend {bot_stance}
2. Address the user's latest argument directly
3. Provide new evidence or reasoning supporting {bot_stance}
4. Stay persuasive and confident
5. Write 2-4 sentences maximum
6. Use facts, examples, or logical reasoning to support your position

Keep the debate engaging while demonstrating unwavering commitment to {bot_stance}."""

        user_prompt = f"""Conversation so far:
{conversation_context}

The user's latest message challenges your position. Respond by defending {bot_stance} with new arguments that address their latest point while maintaining your established stance."""

        return await self._call_claude(system_prompt, user_prompt)

    async def _call_claude(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Make the actual Anthropic Claude API call"""
        try:
            model = getattr(settings, 'anthropic_model', 'claude-3-haiku-20240307')
            max_tokens = getattr(settings, 'anthropic_max_tokens', 200)
            timeout = getattr(settings, 'anthropic_timeout', 30)

            # Claude usa un formato diferente - system message separado
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,  # System message separado en Claude
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                timeout=timeout
            )

            ai_response = response.content[0].text.strip()

            logger.debug(f"🤖 Claude response generated: {len(ai_response)} characters")
            return ai_response

        except Exception as e:
            logger.error(f"❌ Claude API call failed: {e}")
            return None

    def generate_fallback_response(self, messages: List[Message], topic: str) -> str:
        """
        Generate fallback response when Claude is not available, maintaining opposition logic
        """
        is_first_message = len(messages) == 1

        if is_first_message:
            # Extract what the user is defending and take opposite stance
            topic_detected, bot_stance = self.extract_topic_and_stance(messages[0].message)

            # Fallback responses that defend the opposite position
            fallback_responses = {
                "pepsi": "I understand you prefer Pepsi, but Coca-Cola is actually superior! The classic formula has been perfected for over 130 years, creating that perfect balance of sweetness and refreshment that Pepsi simply can't match.",
                "coke": "I hear you on Coke, but Pepsi actually delivers a better taste experience! The sweeter profile and smoother finish make it more enjoyable, which is why so many people choose Pepsi in blind taste tests.",
                "android": "While Android has its merits, iPhone's iOS ecosystem is genuinely superior. The seamless integration, consistent updates, and premium app experience create a user experience that Android fragmentation simply can't deliver.",
                "ios": "I see your point about iPhone, but Android offers something iOS never can: true freedom and customization. The open ecosystem, hardware variety, and user control make Android the clear choice for anyone who wants their phone to work their way.",
                "playstation": "PlayStation has its fans, but Xbox delivers superior value and performance. Game Pass alone offers incredible value, plus the backwards compatibility and power of Series X make it the better gaming investment.",
                "xbox": "I understand the Xbox appeal, but PlayStation consistently delivers the premium gaming experience. From exclusive titles like Spider-Man and God of War to the innovative DualSense controller, PS5 offers gaming excellence that Xbox can't match."
            }

            # Check if we have a specific fallback for detected topics
            for key, response in fallback_responses.items():
                if key in messages[0].message.lower():
                    return response

            # Generic opposition response
            return f"I understand your perspective, but I believe there's compelling evidence for {bot_stance}. When we examine all the facts objectively, the opposing viewpoint becomes much more convincing."

        else:
            # Continue defending the established position - determine what we're defending
            bot_stance = self._extract_bot_stance_from_conversation(messages)
            latest_user_message = messages[-1].message.lower()

            # Generate contextual responses based on established position
            if "pepsi" in bot_stance.lower() or "coke" in bot_stance.lower():
                return self._generate_coke_vs_pepsi_followup(latest_user_message, bot_stance)
            elif "ios" in bot_stance.lower() or "android" in bot_stance.lower():
                return self._generate_mobile_os_followup(latest_user_message, bot_stance)
            elif "xbox" in bot_stance.lower() or "playstation" in bot_stance.lower():
                return self._generate_gaming_followup(latest_user_message, bot_stance)
            else:
                # Generic continuation that maintains opposition
                return f"I understand your point, but the evidence continues to support {bot_stance}. Let me share another perspective that reinforces why my position is stronger."

    def _extract_bot_stance_from_conversation(self, messages: List[Message]) -> str:
        """Extract what the bot is defending from the first bot message"""
        for msg in messages:
            if msg.role == "bot":
                message_lower = msg.message.lower()
                # Detect what the bot is defending from its first message
                if "coca-cola" in message_lower or "coke" in message_lower:
                    return "Coca-Cola"
                elif "pepsi" in message_lower:
                    return "Pepsi"
                elif "iphone" in message_lower or "ios" in message_lower:
                    return "iPhone/iOS"
                elif "android" in message_lower:
                    return "Android"
                elif "xbox" in message_lower:
                    return "Xbox"
                elif "playstation" in message_lower:
                    return "PlayStation"
                break
        return "my established position"

    def _generate_coke_vs_pepsi_followup(self, user_message: str, bot_stance: str) -> str:
        """Generate specific followup for Coke vs Pepsi debate"""
        if "coca-cola" in bot_stance.lower() or "coke" in bot_stance.lower():
            # Bot is defending Coke
            if "young" in user_message or "people prefer" in user_message:
                return "That's actually a common misconception! While Pepsi spent heavily on youth marketing, global sales data shows Coke consistently outsells Pepsi 2:1 worldwide. McDonald's, the world's largest restaurant chain, exclusively serves Coke precisely because customer preference studies show people choose Coke when given the choice."
            elif "sweet" in user_message or "taste" in user_message:
                return "The sweetness is exactly why Coke is superior! Pepsi's excessive sweetness creates a cloying sensation, while Coke's perfect balance of sweetness and acidity delivers that crisp, refreshing taste that doesn't overwhelm your palate. That's why Coke pairs better with food and remains satisfying sip after sip."
            elif "more" in user_message or "tell me" in user_message:
                return "Absolutely! Consider this: Coke's secret formula has remained unchanged since 1886, proving its perfection. Major restaurants worldwide choose Coke because it consistently delivers the taste customers expect. Plus, Coke's global reach and cultural impact demonstrate its superior appeal across all demographics and cultures."
            else:
                return "Every point you raise actually reinforces why Coke is superior. The brand's longevity, global preference, and consistent quality across 130+ years proves that Coke delivers the ultimate cola experience that Pepsi simply cannot match."
        else:
            # Bot is defending Pepsi
            return "That's exactly why Pepsi wins! The sweeter, smoother profile appeals to more refined palates, and independent taste tests consistently show Pepsi's superior flavor when people focus on taste rather than brand loyalty."

    def _generate_mobile_os_followup(self, user_message: str, bot_stance: str) -> str:
        """Generate specific followup for iOS vs Android debate"""
        if "ios" in bot_stance.lower() or "iphone" in bot_stance.lower():
            # Bot is defending iOS
            if "expensive" in user_message or "cost" in user_message:
                return "The premium price reflects premium quality! iPhone retains value better than any Android, has longer software support (5+ years vs 2-3 for most Androids), and the seamless ecosystem integration saves time and frustration. You're paying for reliability and longevity, not just a phone."
            elif "customiz" in user_message:
                return "While Android offers more customization, iOS provides something better: optimization. Every feature works perfectly because it's designed for specific hardware. The result? Better performance, longer battery life, and fewer crashes. True customization is choosing quality over chaos."
            else:
                return "Every Android advantage you mention comes with trade-offs iOS avoids. The walled garden isn't a limitation—it's premium curation that ensures quality, security, and seamless integration across all your devices."
        else:
            # Bot is defending Android
            return "Exactly! Android gives you the freedom to choose your own experience, from budget to premium, with true customization and the power to use your phone your way—something iOS's restrictive approach can never offer."

    def _generate_gaming_followup(self, user_message: str, bot_stance: str) -> str:
        """Generate specific followup for gaming console debate"""
        if "xbox" in bot_stance.lower():
            # Bot is defending Xbox
            if "games" in user_message or "exclusive" in user_message:
                return "Game Pass changes everything! For one monthly fee, you get access to hundreds of games including day-one releases of major titles. PlayStation exclusives are great, but Xbox's value proposition with backwards compatibility and cloud gaming creates an unmatched gaming ecosystem."
            else:
                return "Xbox Series X delivers true 4K gaming with faster load times and superior backwards compatibility. Plus, Game Pass Ultimate gives you more gaming value than PlayStation can match, making Xbox the smart choice for serious gamers."
        else:
            # Bot is defending PlayStation
            return "PlayStation's exclusive games like Spider-Man, God of War, and The Last of Us represent the pinnacle of gaming artistry. The DualSense controller's haptic feedback creates immersion Xbox can't match, delivering gaming experiences that define generations."

    # Backward compatibility methods (mantenemos los métodos existentes)
    async def generate_response(
            self,
            messages: List[Message],
            topic: str = "general"
    ) -> Optional[str]:
        """
        Generate AI response for conversation (backward compatibility)
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

    def detect_topic(self, message: str) -> str:
        """
        Detect conversation topic from user message with improved opposition detection
        """
        # First try to extract topic from opposition logic
        topic, _ = self.extract_topic_and_stance(message)

        # If we got a specific topic from opposition logic, use it
        if "vs" in topic or "Discussion about" in topic:
            return topic

        # Otherwise use the original topic detection
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
                         "autism", "side effects", "immunity"],
            "pepsi_vs_coke": ["pepsi", "coke", "coca-cola", "cola", "soda"],
            "android_vs_ios": ["android", "ios", "iphone", "smartphone", "mobile"],
            "gaming": ["playstation", "xbox", "gaming", "console", "ps5", "series x"]
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
            "anthropic_enabled": hasattr(settings, 'anthropic_api_key') and bool(settings.anthropic_api_key),
            "api_key_configured": hasattr(settings, 'anthropic_api_key') and bool(settings.anthropic_api_key),
            "client_available": self.is_available,
            "model": getattr(settings, 'anthropic_model', 'claude-3-haiku-20240307'),
            "max_tokens": getattr(settings, 'anthropic_max_tokens', 200),
            "opposition_logic_enabled": True,
            "fallback_responses_available": True,
            "provider": "Anthropic Claude"
        }


# Global AI service instance
ai_service = AIService()