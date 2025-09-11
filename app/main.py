# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models.chat_models import ChatRequest, ChatResponse, ConversationStats
from app.services.conversation_service import conversation_service
from app.services.redis_service import redis_service
from app.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Kopi Chatbot API",
    description="API for a persuasive chatbot that can hold debates",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("🚀 Starting Kopi Chatbot API v2.0.0")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Redis URL: {settings.redis_url}")

    # Test Redis connection
    if redis_service.is_connected():
        logger.info("✅ Redis connection successful")
    else:
        logger.warning("⚠️ Redis connection failed - running in fallback mode")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Kopi Chatbot API is running",
        "version": "2.0.0",
        "redis_status": "connected" if redis_service.is_connected() else "disconnected"
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    redis_stats = redis_service.get_conversation_stats()

    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": settings.environment,
        "redis": redis_stats,
        "config": {
            "conversation_ttl": settings.conversation_ttl_seconds,
            "max_messages": settings.max_conversation_messages
        }
    }


@app.get("/stats", response_model=ConversationStats)
async def get_stats():
    """Get conversation statistics"""
    redis_stats = redis_service.get_conversation_stats()

    return ConversationStats(
        total_conversations=redis_stats.get("conversations", 0),
        redis_status=redis_stats.get("status", "unknown"),
        system_info=redis_stats.get("redis_info", {})
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint with Redis persistence
    """
    try:
        logger.info(f"Processing chat request for conversation: {request.conversation_id}")

        response = await conversation_service.process_chat_message(request)

        logger.info(f"Chat response generated for conversation: {response.conversation_id}")
        return response

    except ValueError as e:
        logger.error(f"Validation error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/chat/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a specific conversation
    """
    try:
        success = redis_service.delete_conversation(conversation_id)

        if success:
            return {"message": f"Conversation {conversation_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Conversation not found")

    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)