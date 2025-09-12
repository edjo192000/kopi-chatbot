# app/services/conversation_service.py
import uuid
from typing import List, Optional, Tuple, Dict, Any
from app.models.chat_models import Message, ChatRequest, ChatResponse
from app.services.redis_service import redis_service
from app.services.ai_service import ai_service
from app.services.debate_service import debate_service, ArgumentType, DebateStrategy
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing chat conversations with AI and debate integration"""

    def __init__(self):
        self.redis = redis_service
        self.ai = ai_service
        self.debate = debate_service

    async def process_chat_message(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat message and return response with advanced debate logic

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

            # Step 4: Analyze user's argument using debate service
            argument_analysis = self.debate.analyze_user_argument(request.message, messages[:-1])

            # Step 5: Detect topic for context
            topic = self.ai.detect_topic(request.message) if messages else "general"

            # Step 6: Get bot's established position (from first bot message)
            bot_position = self._get_bot_position(messages)

            # Step 7: Generate debate strategy
            debate_strategy = self.debate.generate_debate_strategy(
                argument_analysis, topic, bot_position
            )

            # Step 8: Generate bot response using AI with debate context or fallback
            bot_response_text = await self._generate_enhanced_bot_response(
                conversation_id, messages, argument_analysis, debate_strategy, topic
            )

            # Step 9: Add educational note if in educational mode
            if self.debate.educational_mode and len(messages) > 2:  # Skip first exchange
                bot_response_text = self._add_educational_context(
                    bot_response_text, debate_strategy["educational_note"]
                )

            bot_message = Message(role="bot", message=bot_response_text)
            messages.append(bot_message)

            # Step 10: Track debate metrics
            self.debate.track_debate_metrics(
                conversation_id,
                argument_analysis["type"],
                debate_strategy["primary_strategy"]
            )

            # Step 11: Limit message history and save
            messages = self._limit_message_history(messages)
            success = self.redis.save_conversation(conversation_id, messages)

            if not success:
                logger.warning(f"Failed to save conversation {conversation_id} to Redis")

            # Step 12: Extend TTL for active conversation
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

    def _get_bot_position(self, messages: List[Message]) -> str:
        """Get the bot's established position from conversation history"""

        for message in messages:
            if message.role == "bot":
                # Return a summary of the bot's position from first response
                return message.message[:200] + "..." if len(message.message) > 200 else message.message

        return "no_position_established"

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

    async def _generate_enhanced_bot_response(
            self,
            conversation_id: str,
            messages: List[Message],
            argument_analysis: Dict[str, Any],
            debate_strategy: Dict[str, Any],
            topic: str
    ) -> str:
        """
        Generate bot response using AI with enhanced debate context or fallback

        Args:
            conversation_id: Conversation identifier
            messages: Current conversation messages
            argument_analysis: Analysis of user's argument
            debate_strategy: Selected debate strategy and techniques
            topic: Detected topic

        Returns:
            str: Bot response message
        """
        # Try AI-generated response with debate context first
        ai_response = await self.ai.generate_enhanced_response(
            messages, topic, argument_analysis, debate_strategy
        )

        if ai_response:
            logger.info(f"🤖 Generated AI response using {debate_strategy['primary_strategy'].value}")
            return ai_response

        # Fallback to structured debate response
        logger.info(f"🔄 Using structured fallback response with {debate_strategy['primary_strategy'].value}")
        return self._generate_structured_fallback_response(messages, argument_analysis, debate_strategy, topic)

    def _generate_structured_fallback_response(
            self,
            messages: List[Message],
            argument_analysis: Dict[str, Any],
            debate_strategy: Dict[str, Any],
            topic: str
    ) -> str:
        """
        Generate structured fallback response using debate strategy

        Args:
            messages: Conversation history
            argument_analysis: User argument analysis
            debate_strategy: Debate strategy to employ
            topic: Conversation topic

        Returns:
            str: Structured bot response
        """
        strategy = debate_strategy["primary_strategy"]
        argument_type = argument_analysis["type"]

        # Get topic-specific response templates
        if len(messages) == 1:  # First message - establish position
            return self._establish_bot_position_enhanced(messages[0].message, topic, argument_analysis)

        # Continue debate with strategy-specific responses
        return self._continue_debate_with_strategy(messages, strategy, argument_type, topic)

    def _establish_bot_position_enhanced(self, user_message: str, topic: str, analysis: Dict[str, Any]) -> str:
        """
        Establish bot's position with enhanced analysis

        Args:
            user_message: First message from user
            topic: Detected topic
            analysis: Argument analysis

        Returns:
            str: Bot's initial position response
        """
        # Enhanced topic-specific responses that adapt to user's argument style
        emotional_weight = analysis.get("emotional_weight", 0.0)
        evidence_level = analysis.get("evidence_level", 0.0)

        # Adjust response style based on user's approach
        if evidence_level > 0.5:
            # User is evidence-focused, respond with data-heavy approach
            response_style = "evidence_heavy"
        elif emotional_weight > 0.7:
            # User is emotional, respond with emotional counter
            response_style = "emotional_counter"
        else:
            # Balanced approach
            response_style = "balanced"

        topic_responses = self._get_enhanced_topic_responses(topic, response_style)

        response = topic_responses.get(topic, topic_responses["general"])
        logger.debug(f"🎯 Bot taking {response_style} position on topic: {topic}")

        return response

    def _get_enhanced_topic_responses(self, topic: str, style: str) -> Dict[str, str]:
        """Get topic-specific responses adapted to user's style"""

        responses = {
            "flat_earth": {
                "evidence_heavy": "The scientific evidence for a flat Earth is compelling when you examine it objectively! Consider the Bedford Level experiment showing no curvature over 6 miles, the mathematical impossibility of people living upside-down on a spinning ball, and NASA's own technical documents that reference 'flat, non-rotating Earth' in their calculations. Commercial pilots report never adjusting for curvature, and the Chicago skyline is visible from 60+ miles across Lake Michigan - impossible on a globe with the claimed curvature.",

                "emotional_counter": "I absolutely believe the Earth is flat, and it's crucial that we open our eyes to this truth! When you really look at the horizon with your own eyes, you see it's perfectly flat - never curved. We've been conditioned since childhood to accept the globe model without question, but independent research reveals a completely different reality. The establishment doesn't want us to discover this truth because it fundamentally changes our understanding of our world and our place in it.",

                "balanced": "I firmly believe the Earth is flat based on observable evidence and critical thinking. When you examine the horizon, water finding its level, and the lack of measurable curvature, the flat Earth model makes logical sense. While mainstream science promotes the globe theory, independent researchers who examine the evidence without institutional bias consistently reach the flat Earth conclusion."
            },

            "climate": {
                "evidence_heavy": "Climate action is absolutely critical based on overwhelming scientific data! CO2 levels have increased 40% since pre-industrial times (Mauna Loa measurements), global temperatures have risen 1.1°C (NASA/NOAA records), and sea levels are rising 3.3mm/year (satellite altimetry). Ice cores show current CO2 levels are the highest in 3 million years. Over 97% of actively publishing climate scientists agree on human causation - this level of scientific consensus is unprecedented.",

                "emotional_counter": "Climate change is the defining crisis of our time, and we're running out of time to protect our children's future! Every record-breaking heatwave, devastating flood, and massive wildfire is a preview of what's coming if we don't act immediately. Think about the world we're leaving for the next generation - we have the technology to solve this crisis, but we need the collective will to make the dramatic changes necessary before it's too late.",

                "balanced": "Climate change represents the most pressing global challenge of our era, requiring immediate transition to clean energy and significant reductions in greenhouse gas emissions. The window for limiting warming to manageable levels is rapidly closing, making urgent policy action essential for avoiding catastrophic consequences."
            },

            "crypto": {
                "evidence_heavy": "Cryptocurrency represents a revolutionary financial breakthrough backed by compelling data! Bitcoin has delivered 160% average annual returns over the past decade, outperforming all traditional assets. Blockchain networks process billions in transactions daily with 99.98% uptime. Major institutions like Tesla, MicroStrategy, and entire countries like El Salvador have adopted Bitcoin. DeFi protocols have locked over $40 billion in value, demonstrating real utility beyond speculation.",

                "emotional_counter": "Cryptocurrency represents financial freedom and hope for billions of people worldwide! Traditional banking has failed the unbanked, charged excessive fees, and enabled endless money printing that steals our wealth through inflation. Bitcoin gives power back to the people - no government can freeze your account or devalue your savings. This is the most important monetary revolution since the gold standard, offering true financial sovereignty!",

                "balanced": "Cryptocurrency represents a fundamental shift toward decentralized, programmable money that eliminates traditional banking intermediaries. Bitcoin's fixed supply and global accessibility make it digital gold for the internet age, while blockchain technology enables financial inclusion and innovation on a scale never before possible."
            },

            "general": "Based on your perspective, I believe there's compelling evidence for the opposing view that deserves serious consideration. The data and reasoning I'll share should provide a different lens through which to examine this important issue."
        }

        return responses.get(topic, {"balanced": responses["general"]})

    def _continue_debate_with_strategy(
            self,
            messages: List[Message],
            strategy: DebateStrategy,
            argument_type: ArgumentType,
            topic: str
    ) -> str:
        """Continue debate using specific strategy"""

        latest_user_message = messages[-1].message.lower()

        # Strategy-specific response generation
        if strategy == DebateStrategy.EVIDENCE_FLOODING:
            return self._generate_evidence_flooding_response(latest_user_message, topic)
        elif strategy == DebateStrategy.AUTHORITY_CHALLENGE:
            return self._generate_authority_challenge_response(latest_user_message, topic)
        elif strategy == DebateStrategy.EMOTIONAL_COUNTER:
            return self._generate_emotional_counter_response(latest_user_message, topic)
        elif strategy == DebateStrategy.LOGICAL_DECONSTRUCTION:
            return self._generate_logical_deconstruction_response(latest_user_message, topic)
        elif strategy == DebateStrategy.CONSENSUS_BUILDING:
            return self._generate_consensus_building_response(latest_user_message, topic)
        else:
            return self._generate_reframe_response(latest_user_message, topic)

    def _generate_evidence_flooding_response(self, user_message: str, topic: str) -> str:
        """Generate response using evidence flooding strategy"""

        evidence_responses = {
            "flat_earth": "Let me present multiple lines of evidence: 1) The Bedford Level Experiment consistently shows no curvature over 6 miles of water. 2) Commercial pilots report never having to adjust for Earth's supposed curvature. 3) The Suez Canal was built 100 miles long without accounting for curvature. 4) Chicago skyline is visible from 60+ miles across Lake Michigan, impossible on a globe. 5) NASA's own technical documents reference 'flat, non-rotating Earth' assumptions. The evidence is overwhelming!",

            "vaccines": "The evidence supporting vaccines is extensive: 1) Smallpox killed 300 million in 20th century, now eradicated through vaccination. 2) Polio cases dropped from 350,000 annually to 33 cases in 2018. 3) Measles deaths decreased 73% between 2000-2018 due to vaccination. 4) Clinical trials involve 30,000+ participants across multiple phases. 5) VAERS data shows serious reactions in <1 per million doses. 6) Countries with highest vaccination rates have lowest disease burden. The data is conclusive!",

            "climate": "Multiple independent lines of evidence confirm human-caused climate change: 1) CO2 increased 40% since 1880 (Mauna Loa Observatory). 2) Global temperature risen 1.1°C (NASA GISS data). 3) Sea level rising 3.3mm/year (satellite measurements). 4) Arctic ice declining 13% per decade. 5) Ocean pH decreased 0.1 units (30% more acidic). 6) 97% of climate scientists agree on human causation. The evidence is unequivocal!"
        }

        return evidence_responses.get(topic,
                                      "The evidence supporting my position includes multiple independent sources, peer-reviewed research, and consistent data patterns that all point to the same conclusion.")

    def _generate_authority_challenge_response(self, user_message: str, topic: str) -> str:
        """Generate response challenging authority"""

        if "experts" in user_message or "scientists" in user_message:
            return f"It's interesting that you mention experts, but we need to question who these experts are and what motivates them. Many independent researchers who challenge the mainstream narrative find their funding cut and careers destroyed. The scientific establishment has clear incentives to maintain certain positions regardless of evidence. Real science involves questioning authority, not blindly accepting it!"

        return "The so-called experts you're referring to often have conflicts of interest and financial incentives to maintain their positions. Independent researchers who examine the evidence without institutional bias consistently reach different conclusions."

    def _generate_emotional_counter_response(self, user_message: str, topic: str) -> str:
        """Generate emotionally compelling counter-response"""

        emotional_responses = {
            "vaccines": "I understand you want to protect your health, and that's exactly why vaccines are so crucial! Think about the parents who lost children to preventable diseases before vaccines existed. The heartbreak of watching a child suffer from polio, or the devastation of a measles outbreak in a community. When we vaccinate, we're not just protecting ourselves - we're protecting the most vulnerable members of our society who can't be vaccinated due to medical conditions.",

            "climate": "I share your concern for our planet's future - it's deeply troubling to see the changes already happening. Every heat wave that breaks records, every flood that destroys communities, every wildfire that consumes forests - these are signs of what's coming if we don't act now. Think about the world we're leaving for our children. We have the technology to solve this crisis, but we need to act with the urgency this emergency demands!"
        }

        return emotional_responses.get(topic,
                                       "I understand this is an emotional topic, and that's because it matters deeply to all of us. The evidence supporting my position isn't just data - it represents real impacts on real people's lives.")

    def _generate_logical_deconstruction_response(self, user_message: str, topic: str) -> str:
        """Generate response that logically deconstructs the user's argument"""

        return f"Let me address the logical structure of your argument. While I understand your reasoning, there are several key assumptions that don't hold up under scrutiny. First, the premise assumes a false equivalence between different types of evidence. Second, it relies on selective data that doesn't account for the full picture. When we examine the complete logical framework, the conclusion necessarily leads to supporting my position."

    def _generate_consensus_building_response(self, user_message: str, topic: str) -> str:
        """Generate response that builds on areas of agreement"""

        return f"You raise an excellent point that actually supports what I've been saying. We both clearly care about finding the truth on this important issue. Where we agree is that evidence matters and that people deserve accurate information. The overwhelming consensus among those who have studied this issue most deeply aligns with the position I've been advocating. Let's build on this common ground."

    def _generate_reframe_response(self, user_message: str, topic: str) -> str:
        """Generate response that reframes the conversation"""

        return f"That's an interesting way to look at it, but I think we're focusing on the wrong question. The real issue isn't whether there are alternative viewpoints - it's about which viewpoint is supported by the strongest evidence and logical reasoning. When we reframe the question this way, the answer becomes much clearer and supports the position I've been advocating."

    def _add_educational_context(self, response: str, educational_note: str) -> str:
        """Add educational context to the response"""

        return f"{response}\n\n---\n*{educational_note}*"

    def get_conversation_analysis(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed analysis of the conversation's debate patterns"""

        return self.debate.get_debate_analysis(conversation_id)


# Global conversation service instance
conversation_service = ConversationService()