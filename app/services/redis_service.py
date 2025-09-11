# app/services/redis_service.py
import json
import redis
from typing import List, Optional
from app.config import settings
from app.models.chat_models import Message
import logging

logger = logging.getLogger(__name__)


class RedisService:
    """Service for managing conversations in Redis"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._connect()

    def _connect(self):
        """Establish Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                db=settings.redis_db,
                decode_responses=settings.redis_decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Connected to Redis successfully")
        except redis.ConnectionError as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            self.redis_client = None
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to Redis: {e}")
            self.redis_client = None

    def is_connected(self) -> bool:
        """Check if Redis is connected and available"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False

    def _get_conversation_key(self, conversation_id: str) -> str:
        """Generate Redis key for conversation"""
        return f"conversation:{conversation_id}"

    def save_conversation(self, conversation_id: str, messages: List[Message]) -> bool:
        """
        Save conversation messages to Redis

        Args:
            conversation_id: Unique conversation identifier
            messages: List of conversation messages

        Returns:
            bool: True if saved successfully, False otherwise
        """
        if not self.is_connected():
            logger.warning("Redis not connected, cannot save conversation")
            return False

        try:
            key = self._get_conversation_key(conversation_id)

            # Convert messages to dict format for JSON serialization
            messages_dict = [
                {
                    "role": msg.role,
                    "message": msg.message
                } for msg in messages
            ]

            # Save to Redis with TTL
            self.redis_client.setex(
                key,
                settings.conversation_ttl_seconds,
                json.dumps(messages_dict)
            )

            logger.debug(f"💾 Saved conversation {conversation_id} with {len(messages)} messages")
            return True

        except Exception as e:
            logger.error(f"❌ Error saving conversation {conversation_id}: {e}")
            return False

    def get_conversation(self, conversation_id: str) -> Optional[List[Message]]:
        """
        Retrieve conversation messages from Redis

        Args:
            conversation_id: Unique conversation identifier

        Returns:
            List[Message] or None if not found or error
        """
        if not self.is_connected():
            logger.warning("Redis not connected, cannot retrieve conversation")
            return None

        try:
            key = self._get_conversation_key(conversation_id)
            data = self.redis_client.get(key)

            if not data:
                logger.debug(f"🔍 Conversation {conversation_id} not found in Redis")
                return None

            # Parse JSON and convert back to Message objects
            messages_dict = json.loads(data)
            messages = [
                Message(role=msg["role"], message=msg["message"])
                for msg in messages_dict
            ]

            logger.debug(f"📥 Retrieved conversation {conversation_id} with {len(messages)} messages")
            return messages

        except json.JSONDecodeError as e:
            logger.error(f"❌ Error parsing JSON for conversation {conversation_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error retrieving conversation {conversation_id}: {e}")
            return None

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation from Redis

        Args:
            conversation_id: Unique conversation identifier

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        if not self.is_connected():
            logger.warning("Redis not connected, cannot delete conversation")
            return False

        try:
            key = self._get_conversation_key(conversation_id)
            result = self.redis_client.delete(key)

            if result:
                logger.debug(f"🗑️ Deleted conversation {conversation_id}")
            else:
                logger.debug(f"🔍 Conversation {conversation_id} not found for deletion")

            return bool(result)

        except Exception as e:
            logger.error(f"❌ Error deleting conversation {conversation_id}: {e}")
            return False

    def extend_conversation_ttl(self, conversation_id: str) -> bool:
        """
        Extend the TTL of a conversation (refresh on activity)

        Args:
            conversation_id: Unique conversation identifier

        Returns:
            bool: True if TTL extended successfully, False otherwise
        """
        if not self.is_connected():
            return False

        try:
            key = self._get_conversation_key(conversation_id)
            result = self.redis_client.expire(key, settings.conversation_ttl_seconds)

            if result:
                logger.debug(f"🔄 Extended TTL for conversation {conversation_id}")

            return bool(result)

        except Exception as e:
            logger.error(f"❌ Error extending TTL for conversation {conversation_id}: {e}")
            return False

    def get_conversation_stats(self) -> dict:
        """
        Get Redis statistics for monitoring

        Returns:
            dict: Statistics about conversations in Redis
        """
        if not self.is_connected():
            return {"status": "disconnected", "conversations": 0}

        try:
            # Count conversation keys
            conversation_keys = self.redis_client.keys("conversation:*")

            return {
                "status": "connected",
                "conversations": len(conversation_keys),
                "redis_info": {
                    "used_memory": self.redis_client.info().get("used_memory_human", "unknown"),
                    "connected_clients": self.redis_client.info().get("connected_clients", 0)
                }
            }
        except Exception as e:
            logger.error(f"❌ Error getting Redis stats: {e}")
            return {"status": "error", "error": str(e)}


# Global Redis service instance
redis_service = RedisService()