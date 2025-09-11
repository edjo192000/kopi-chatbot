# app/models/chat_models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class Message(BaseModel):
    """Individual message in a conversation"""
    role: Literal["user", "bot"] = Field(..., description="Message sender role")
    message: str = Field(..., min_length=1, max_length=2000, description="Message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Message timestamp")

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID, null for new conversation")
    message: str = Field(..., min_length=1, max_length=2000, description="User message content")

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    conversation_id: str = Field(..., description="Conversation unique identifier")
    messages: List[Message] = Field(..., description="Conversation message history (last 5 pairs)")

class ConversationStats(BaseModel):
    """Statistics about the conversation system"""
    total_conversations: int = Field(..., description="Total active conversations")
    redis_status: str = Field(..., description="Redis connection status")
    system_info: dict = Field(default_factory=dict, description="Additional system information")