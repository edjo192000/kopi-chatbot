# app/services/conversation_service.py
import uuid
from typing import List, Optional, Tuple
from app.models.chat_models import Message, ChatRequest, ChatResponse
from app.services.redis_service import redis_service
from app.services.ai_service import ai_service
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing chat conversations with AI integration"""

    def __init__(self):
        self.redis = redis_service
        self.ai = ai_service

    async def process_chat_message(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat message and return response with AI integration

        Args:
            request: Chat request with message and optional conversation_id

        Returns:
            ChatResponse: Response with conversation_id and message history

        Raises:
            ValueError: If message processing fails
        """
        try:
            # Step 1: Get or create conversation ID
            conversation_id = request.conversation_id or str(uuid.uuid4())

            # Step 2: Retrieve existing conversation or create new one
            messages = self._get_or_create_conversation(conversation_id)

            # Step 3: Add user message
            user_message = Message(role="user", message=request.message)
            messages.append(user_message)

            # Step 4: Generate bot response using AI or fallback
            bot_response_text = await self._generate_bot_response(conversation_id, messages)
            bot_message = Message(role="bot", message=bot_response_text)
            messages.append(bot_message)

            # Step 5: Limit message history and save
            messages = self._limit_message_history(messages)
            success = self.redis.save_conversation(conversation_id, messages)

            if not success:
                logger.warning(f"Failed to save conversation {conversation_id} to Redis")

            # Step 6: Extend TTL for active conversation
            self.redis.extend_conversation_ttl(conversation_id)

            return ChatResponse(
                conversation_id=conversation_id,
                messages=messages
            )

        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            raise ValueError(f"Failed to process chat message: {str(e)}")

    def _get_or_create_conversation(self, conversation_id: str) -> List[Message]:
        """
        Retrieve existing conversation or create new empty one

        Args:
            conversation_id: Conversation identifier

        Returns:
            List[Message]: Existing messages or empty list
        """
        if conversation_id:
            messages = self.redis.get_conversation(conversation_id)
            if messages is not None:
                logger.debug(f"📥 Retrieved existing conversation {conversation_id}")
                return messages

        logger.debug(f"🆕 Creating new conversation {conversation_id}")
        return []

    def _limit_message_history(self, messages: List[Message]) -> List[Message]:
        """
        Limit conversation to last N messages

        Args:
            messages: Full message list

        Returns:
            List[Message]: Limited message list
        """
        max_messages = settings.max_conversation_messages
        if len(messages) > max_messages:
            # Keep the most recent messages
            limited_messages = messages[-max_messages:]
            logger.debug(f"✂️ Limited conversation to {len(limited_messages)} messages")
            return limited_messages
        return messages

    async def _generate_bot_response(self, conversation_id: str, messages: List[Message]) -> str:
        """
        Generate bot response using AI or fallback to hardcoded responses

        Args:
            conversation_id: Conversation identifier
            messages: Current conversation messages

        Returns:
            str: Bot response message
        """
        # Detect topic for better AI responses
        topic = self.ai.detect_topic(messages[-1].message) if messages else "general"

        # Try AI-generated response first
        ai_response = await self.ai.generate_response(messages, topic)

        if ai_response:
            logger.info(f"🤖 Generated AI response for topic: {topic}")
            return ai_response

        # Fallback to hardcoded responses
        logger.info(f"🔄 Using fallback response for topic: {topic}")
        return self._generate_fallback_response(messages, topic)

    def _generate_fallback_response(self, messages: List[Message], topic: str) -> str:
        """
        Generate fallback response when AI is unavailable

        Args:
            messages: Current conversation messages
            topic: Detected topic

        Returns:
            str: Fallback response message
        """
        # Check if this is the first message (establish position)
        if len(messages) == 1:
            return self._establish_bot_position(messages[0].message, topic)

        # Continue existing debate
        return self._continue_debate(messages, topic)

    def _establish_bot_position(self, user_message: str, topic: str) -> str:
        """
        Establish bot's position based on the first user message and detected topic

        Args:
            user_message: First message from user
            topic: Detected topic

        Returns:
            str: Bot's initial position response
        """
        # Enhanced topic-specific responses
        topic_responses = {
            "flat_earth": """I absolutely believe the Earth is flat! The evidence is overwhelming when you really look at it. Think about it - when you look at the horizon, does it curve? No! It's perfectly flat. NASA and space agencies have been deceiving us with CGI and fake images for decades. The fact that water always finds its level proves we're not living on a spinning ball. Have you ever felt the Earth spinning at 1,000 mph? Of course not, because we're on a stationary plane!""",

            "vaccines": """Vaccines are absolutely one of humanity's greatest medical achievements! They have saved millions of lives and practically eradicated deadly diseases like smallpox and polio. The scientific evidence is overwhelming - vaccines are safe, effective, and essential for public health. The rare side effects are minimal compared to the devastating diseases they prevent. Anti-vaccine misinformation has led to outbreaks of preventable diseases. We should trust the decades of rigorous scientific research and the consensus of medical professionals worldwide!""",

            "climate": """Climate change is the most pressing issue of our time, and human activity is undeniably the primary cause! The scientific consensus is crystal clear - 97% of climate scientists agree. We're seeing unprecedented warming, melting ice caps, rising sea levels, and extreme weather events. The evidence from ice cores, temperature records, and atmospheric CO2 measurements is irrefutable. We need immediate, dramatic action to transition to renewable energy and reduce emissions, or we face catastrophic consequences for future generations!""",

            "crypto": """Cryptocurrency represents the future of money and financial freedom! Bitcoin and blockchain technology are revolutionary - they eliminate the need for banks and government control over our finances. It's decentralized, transparent, and gives power back to the people. Traditional banking systems are outdated and corrupt. Crypto offers financial inclusion for the unbanked, protection against inflation, and true ownership of your wealth. The volatility is just growing pains - in 10 years, we'll all be using digital currencies!""",

            "general": f"""That's a fascinating topic you've brought up! Based on what you've said, I have to strongly disagree with your perspective. Let me explain why I believe the opposite view is not only correct, but absolutely essential to understand. The evidence clearly supports a completely different conclusion than what you've suggested, and I'm confident I can convince you to see this matter from a much more informed angle."""
        }

        response = topic_responses.get(topic, topic_responses["general"])
        logger.debug(f"🎯 Bot taking position on topic: {topic}")
        return response

    def _continue_debate(self, messages: List[Message], topic: str) -> str:
        """
        Continue the debate while maintaining the bot's position

        Args:
            messages: Full conversation history
            topic: Detected topic

        Returns:
            str: Bot's continued argument
        """
        # Get user's latest message
        latest_user_message = messages[-1].message.lower()

        # Topic-specific continuation responses
        if topic == "flat_earth":
            return self._continue_flat_earth_debate(latest_user_message)
        elif topic == "vaccines":
            return self._continue_vaccine_debate(latest_user_message)
        elif topic == "climate":
            return self._continue_climate_debate(latest_user_message)
        elif topic == "crypto":
            return self._continue_crypto_debate(latest_user_message)

        # Generic continuation responses
        import random
        persuasive_responses = [
            "I understand your skepticism, but the evidence I've presented is irrefutable. Let me address your concerns with even more compelling facts that will change your perspective completely.",
            "You raise an interesting point, but it actually reinforces my argument when you examine it more closely. Consider this additional evidence that supports my position.",
            "I appreciate your perspective, but I think you're missing some crucial information that would change your mind completely. Here's what the data really shows.",
            "That's exactly the kind of thinking that needs to be challenged! Let me show you why that assumption is fundamentally flawed and what the real evidence reveals.",
            "I can see why you might think that, but the comprehensive research tells a completely different story. Here's what you need to understand."
        ]

        return random.choice(persuasive_responses)

    def _continue_flat_earth_debate(self, user_message: str) -> str:
        """Continue flat earth debate with contextual responses"""
        if any(word in user_message for word in ["satellite", "space", "nasa", "photo", "image"]):
            return "Those so-called 'satellite images' are all CGI! NASA admits they composite these images - they're not real photographs. If Earth were really a globe, why can't we see the curve from airplane windows at 35,000 feet? The horizon always appears flat and rises to eye level, exactly as it would on a flat plane. Real pilots know this - they never have to adjust for curvature when flying long distances!"

        elif any(word in user_message for word in ["gravity", "physics", "science"]):
            return "Gravity is just a theory that's never been proven! What we experience is simply density and buoyancy - objects fall because they're denser than air, not because of some mysterious force pulling everything to a spinning ball. If gravity were real, how could a tiny butterfly fly upward against this supposed massive force? The scientific establishment pushes gravity to support their globe lie!"

        return "The more you research flat earth with an open mind, the more obvious it becomes that we've been deceived. Every piece of evidence supports a flat, stationary plane covered by a dome firmament. Ships don't disappear over a curve - they fade from view due to atmospheric perspective and the limitations of human vision!"

    def _continue_vaccine_debate(self, user_message: str) -> str:
        """Continue vaccine debate with contextual responses"""
        if any(word in user_message for word in ["side effects", "adverse", "reactions", "harm"]):
            return "While it's true that vaccines can have side effects, they're extraordinarily rare compared to the diseases they prevent. For example, severe allergic reactions occur in about 1 in a million doses, while diseases like measles killed 2.6 million people annually before vaccination. The monitoring systems like VAERS track every possible side effect, making vaccines among the most thoroughly monitored medical interventions in history!"

        elif any(word in user_message for word in ["natural immunity", "immune system"]):
            return "Natural immunity is indeed powerful, but it comes at a tremendous cost! To get natural immunity to measles, you risk brain damage, pneumonia, and death. Vaccines give you the immunity without the disease. Your immune system is amazing, and vaccines work WITH it, training it to recognize threats safely. It's like giving your immune system a practice run before the real battle!"

        return "The overwhelming scientific evidence from hundreds of studies involving millions of people proves vaccines are safe and effective. Countries with high vaccination rates have virtually eliminated diseases that once killed thousands. The benefits far outweigh any minimal risks, and herd immunity protects our most vulnerable community members!"

    def _continue_climate_debate(self, user_message: str) -> str:
        """Continue climate debate with contextual responses"""
        if any(word in user_message for word in ["natural", "cycles", "sun"]):
            return "While Earth does have natural climate cycles, the current warming is happening far too rapidly to be natural! Solar activity has actually been decreasing slightly over the past 40 years, yet temperatures continue to rise. Ice core data shows that natural climate changes occur over thousands of years, not decades. The correlation between CO2 emissions and temperature rise is undeniable - we've increased atmospheric CO2 by 40% since pre-industrial times!"

        elif any(word in user_message for word in ["expensive", "economy", "jobs"]):
            return "The cost of action is far less than the cost of inaction! Extreme weather events already cost billions annually. The renewable energy sector is creating millions of jobs and is now cheaper than fossil fuels in many markets. Countries leading in clean energy are becoming more competitive, not less. Climate action is an economic opportunity, not a burden - early movers will dominate the trillion-dollar clean energy market!"

        return "Every additional year we delay action makes the problem exponentially worse and more expensive to solve. We're already seeing the devastating effects - record heat waves, unprecedented flooding, and ecosystem collapse. The window for limiting warming to manageable levels is rapidly closing. We need bold action now!"

    def _continue_crypto_debate(self, user_message: str) -> str:
        """Continue crypto debate with contextual responses"""
        if any(word in user_message for word in ["volatile", "unstable", "risky"]):
            return "Volatility is normal for any revolutionary technology in its early stages! The internet stocks were incredibly volatile in the 1990s, but look at them now. Bitcoin has outperformed every traditional asset class over the past decade despite volatility. As adoption increases and the market matures, volatility decreases. Major institutions like Tesla, MicroStrategy, and even countries like El Salvador are adopting Bitcoin - they wouldn't do this if it were just speculation!"

        elif any(word in user_message for word in ["energy", "environment", "mining"]):
            return "Bitcoin mining is actually driving renewable energy adoption! Miners seek the cheapest energy, which is increasingly renewable. Bitcoin mining can monetize stranded renewable energy and provide grid stability. Traditional banking uses far more energy when you account for bank branches, ATMs, data centers, and employee commutes. Plus, Bitcoin incentivizes innovation in clean energy solutions!"

        return "Cryptocurrency isn't just about investment returns - it's about financial sovereignty and freedom! With traditional currencies, governments can print money endlessly, devaluing your savings. Bitcoin has a fixed supply of 21 million coins - it's digital gold that can't be manipulated by central banks. It enables financial inclusion for billions of unbanked people worldwide!"


# Global conversation service instance
conversation_service = ConversationService()