# app/services/conversation_service.py
import uuid
from typing import List, Optional, Tuple, Dict, Any
from app.models.chat_models import Message, ChatRequest, ChatResponse
from app.services.redis_service import redis_service
from app.services.ai_service import ai_service
from app.services.meta_persuasion_service import meta_persuasion_service
from app.config import settings
import logging
import random

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing chat conversations with AI and meta-persuasion integration"""

    def __init__(self):
        self.redis = redis_service
        self.ai = ai_service
        self.meta_persuasion = meta_persuasion_service

    async def process_chat_message(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat message and return response with meta-persuasion analysis

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

            # Step 4: Analyze user's persuasion techniques using meta-persuasion service
            user_persuasion_analysis = self.meta_persuasion.analyze_persuasion_techniques(request.message)

            # Step 5: Detect topic for context
            topic = self.ai.detect_topic(request.message) if len(messages) == 1 else self._get_conversation_topic(
                messages)

            # Step 6: Get bot's established position (from first bot message)
            bot_position = self._get_bot_position(messages)

            # Step 7: Check if educational mode should be enabled
            should_add_educational_content = self._should_add_educational_content(
                user_persuasion_analysis, len(messages)
            )

            # Step 8: Generate bot response
            if should_add_educational_content:
                # Use meta-persuasion service for educational response
                educational_response = self.meta_persuasion.create_educational_response(
                    request.message, messages[:-1], topic
                )
                bot_response_text = educational_response["response"]
                meta_analysis = educational_response
            else:
                # Use standard enhanced response with mock analysis for AI service
                mock_argument_analysis = self._create_mock_argument_analysis(user_persuasion_analysis)
                mock_debate_strategy = self._create_mock_debate_strategy(user_persuasion_analysis, topic)

                bot_response_text = await self._generate_enhanced_bot_response(
                    conversation_id, messages, mock_argument_analysis, mock_debate_strategy, topic
                )
                meta_analysis = None

            # Step 9: Add educational context if meta-persuasion was used
            if should_add_educational_content and meta_analysis:
                educational_note = self._generate_educational_note(meta_analysis)
                bot_response_text = self._add_educational_context(bot_response_text, educational_note)

            bot_message = Message(role="bot", message=bot_response_text)
            messages.append(bot_message)

            # Step 10: Store meta-persuasion analysis for conversation analysis
            if meta_analysis:
                self._store_meta_persuasion_analysis(conversation_id, meta_analysis)

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
                logger.debug(f"Retrieved existing conversation {conversation_id}")
                return messages

        logger.debug(f"Creating new conversation {conversation_id}")
        return []

    def _get_bot_position(self, messages: List[Message]) -> str:
        """Get the bot's established position from conversation history"""
        for message in messages:
            if message.role == "bot":
                return message.message[:200] + "..." if len(message.message) > 200 else message.message
        return "no_position_established"

    def _get_conversation_topic(self, messages: List[Message]) -> str:
        """Get the established topic from conversation history"""
        if messages and len(messages) > 0:
            first_user_message = next((msg for msg in messages if msg.role == "user"), None)
            if first_user_message:
                return self.ai.detect_topic(first_user_message.message)
        return "general"

    def _should_add_educational_content(
            self,
            user_persuasion_analysis: Dict[str, Any],
            message_count: int
    ) -> bool:
        """Determine if educational content should be added to response"""
        if not self.meta_persuasion.demonstration_mode:
            return False

        high_technique_usage = len(user_persuasion_analysis.get("techniques_detected", [])) >= 2
        high_persuasion_score = user_persuasion_analysis.get("persuasion_score", 0) > 0.6
        not_first_exchange = message_count > 2

        # Random chance to add educational content (30%) to keep it interesting
        random_chance = random.random() < 0.3

        return (high_technique_usage or high_persuasion_score or random_chance) and not_first_exchange

    def _create_mock_argument_analysis(self, user_persuasion_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create mock argument analysis for AI service compatibility"""
        return {
            "type": "general",
            "user_techniques": user_persuasion_analysis.get("techniques_detected", []),
            "emotional_weight": sum(user_persuasion_analysis.get("emotional_appeals", {}).values()),
            "evidence_level": 0.5 if user_persuasion_analysis.get("credibility_signals", []) else 0.3
        }

    def _create_mock_debate_strategy(self, user_persuasion_analysis: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Create mock debate strategy for AI service compatibility"""
        return {
            "primary_strategy": "logical_structure",
            "techniques": user_persuasion_analysis.get("techniques_detected", [])[:3],
            "educational_note": "Demonstrating counter-persuasion techniques"
        }

    def _limit_message_history(self, messages: List[Message]) -> List[Message]:
        """Limit conversation to last N messages"""
        max_messages = settings.max_conversation_messages
        if len(messages) > max_messages:
            limited_messages = messages[-max_messages:]
            logger.debug(f"Limited conversation to {len(limited_messages)} messages")
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
        """Generate bot response using AI with enhanced context or fallback with opposition logic"""

        # Try AI-generated response first
        ai_response = await self.ai.generate_enhanced_response(
            messages, topic, argument_analysis, debate_strategy
        )

        if ai_response:
            logger.info(f"Generated AI response using enhanced method")
            return ai_response

        # Use AI service fallback (which now includes opposition logic)
        logger.info(f"Using AI service fallback with opposition logic")
        fallback_response = self.ai.generate_fallback_response(messages, topic)
        return fallback_response

    def _generate_structured_fallback_response(
            self,
            messages: List[Message],
            argument_analysis: Dict[str, Any],
            topic: str
    ) -> str:
        """Generate structured fallback response (DEPRECATED - use AI service fallback instead)"""

        # This method is now deprecated in favor of AI service fallback
        # But kept for backward compatibility
        return self.ai.generate_fallback_response(messages, topic)

    def _establish_bot_position(self, user_message: str, topic: str) -> str:
        """Establish bot's initial position (DEPRECATED - use AI service fallback instead)"""

        # This method is now deprecated in favor of AI service fallback
        # But kept for backward compatibility
        from app.models.chat_models import Message
        mock_messages = [Message(role="user", message=user_message)]
        return self.ai.generate_fallback_response(mock_messages, topic)

    def _continue_debate_structured(self, messages: List[Message], topic: str) -> str:
        """Continue debate with structured response (DEPRECATED - use AI service fallback instead)"""

        # This method is now deprecated in favor of AI service fallback
        # But kept for backward compatibility
        return self.ai.generate_fallback_response(messages, topic)

    def _generate_educational_note(self, meta_analysis: Dict[str, Any]) -> str:
        """Generate educational note from meta-persuasion analysis"""

        techniques_demo = meta_analysis.get("techniques_demonstrated", [])
        user_analysis = meta_analysis.get("user_analysis", {})
        user_techniques = user_analysis.get("techniques_detected", [])

        note_parts = []

        if user_techniques:
            user_technique_names = [t.value if hasattr(t, 'value') else str(t) for t in user_techniques]
            note_parts.append(f"Your message used: {', '.join(user_technique_names)}")

        if techniques_demo:
            note_parts.append(f"My response demonstrated: {', '.join(techniques_demo)}")

        if not note_parts:
            note_parts.append("This exchange demonstrates various persuasion techniques in action")

        return " | ".join(note_parts)

    def _add_educational_context(self, response: str, educational_note: str) -> str:
        """Add educational context to the response"""
        return f"{response}\n\n---\n*Educational note: {educational_note}*"

    def _store_meta_persuasion_analysis(
            self,
            conversation_id: str,
            meta_analysis: Dict[str, Any]
    ) -> bool:
        """Store meta-persuasion analysis for later retrieval"""

        try:
            analysis_key = f"meta_analysis:{conversation_id}"

            if self.redis.is_connected():
                import json
                self.redis.redis_client.setex(
                    analysis_key,
                    settings.conversation_ttl_seconds,
                    json.dumps(meta_analysis, default=str)
                )
                logger.debug(f"Stored meta-persuasion analysis for {conversation_id}")
                return True
        except Exception as e:
            logger.error(f"Error storing meta-persuasion analysis: {e}")

        return False

    def get_meta_persuasion_analysis(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve meta-persuasion analysis for a conversation"""

        try:
            analysis_key = f"meta_analysis:{conversation_id}"

            if self.redis.is_connected():
                import json
                data = self.redis.redis_client.get(analysis_key)
                if data:
                    return json.loads(data)
        except Exception as e:
            logger.error(f"Error retrieving meta-persuasion analysis: {e}")

        return None

    def get_conversation_analysis(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed analysis of the conversation's patterns"""

        # Get conversation messages
        messages = self.redis.get_conversation(conversation_id)
        if not messages:
            return None

        # Get meta-persuasion analysis
        meta_analysis = self.get_meta_persuasion_analysis(conversation_id)

        # Analyze all messages
        message_analyses = []
        for msg in messages:
            analysis = self.meta_persuasion.analyze_persuasion_techniques(msg.message)
            message_analyses.append({
                "role": msg.role,
                "message": msg.message[:100] + "..." if len(msg.message) > 100 else msg.message,
                "analysis": analysis
            })

        return {
            "conversation_id": conversation_id,
            "message_count": len(messages),
            "message_analyses": message_analyses,
            "meta_persuasion_analysis": meta_analysis,
            "conversation_stats": {
                "total_techniques_detected": sum(
                    len(ma["analysis"].get("techniques_detected", []))
                    for ma in message_analyses
                ),
                "average_persuasion_score": sum(
                    ma["analysis"].get("persuasion_score", 0)
                    for ma in message_analyses
                ) / len(message_analyses) if message_analyses else 0
            }
        }


# Global conversation service instance
conversation_service = ConversationService()