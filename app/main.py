# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.models.chat_models import ChatRequest, ChatResponse, ConversationStats
from app.services.conversation_service import conversation_service
from app.services.redis_service import redis_service
from app.services.ai_service import ai_service
from app.services.meta_persuasion_service import meta_persuasion_service, PersuasionTechnique
from app.config import settings
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=getattr(settings, 'log_level', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting Kopi Chatbot API v2.0 with Meta-Persuasion")
    logger.info(f"📊 Redis status: {'connected' if redis_service.is_connected() else 'disconnected'}")
    logger.info(f"🤖 AI service: {'available' if ai_service.is_available else 'fallback mode'}")
    logger.info(f"🎭 Meta-persuasion: {'enabled' if meta_persuasion_service.demonstration_mode else 'disabled'}")

    yield

    # Shutdown
    logger.info("⏹️ Shutting down Kopi Chatbot API")


# Create FastAPI application
app = FastAPI(
    title="Kopi Chatbot API",
    description="A persuasive chatbot API with meta-persuasion analysis capabilities",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Kopi Chatbot API v2.0 - Meta-Persuasion Enabled",
        "version": "2.0.0",
        "status": "active",
        "features": [
            "AI-powered conversations",
            "Persistent chat history",
            "Meta-persuasion analysis",
            "Educational content",
            "Debate techniques"
        ],
        "endpoints": {
            "chat": "/chat",
            "analyze": "/analyze",
            "demonstrate": "/demonstrate",
            "techniques": "/techniques",
            "conversation_analysis": "/conversation/{id}/analysis",
            "health": "/health",
            "stats": "/stats"
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint for conversational AI with integrated meta-persuasion analysis
    """
    try:
        logger.info(f"📧 Processing chat request: {len(request.message)} chars")
        response = await conversation_service.process_chat_message(request)
        logger.info(f"✅ Chat response generated: {response.conversation_id}")
        return response
    except ValueError as e:
        logger.error(f"❌ Validation error in chat: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Unexpected error in chat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/analyze")
async def analyze_message_endpoint(request: dict) -> dict:
    """
    Analyze a message for persuasion techniques and debate characteristics

    Body:
    {
        "message": "text to analyze"
    }
    """
    try:
        message = request.get("message", "")
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        if len(message) > 2000:
            raise HTTPException(status_code=400, detail="Message too long (max 2000 characters)")

        # Get persuasion technique analysis
        persuasion_analysis = meta_persuasion_service.analyze_persuasion_techniques(message)

        # Get topic detection
        topic = ai_service.detect_topic(message)

        analysis_result = {
            "message": message,
            "topic": topic,
            "persuasion_analysis": persuasion_analysis,
            "analysis_summary": {
                "technique_count": len(persuasion_analysis.get("techniques_detected", [])),
                "persuasion_score": persuasion_analysis.get("persuasion_score", 0),
                "primary_emotions": [
                    emotion for emotion, score in persuasion_analysis.get("emotional_appeals", {}).items()
                    if score > 0.3
                ],
                "credibility_signals": persuasion_analysis.get("credibility_signals", [])
            },
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"📊 Message analysis completed for {len(message)} char message")
        return analysis_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in message analysis: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")


@app.post("/demonstrate")
async def demonstrate_technique_endpoint(request: dict) -> dict:
    """
    Demonstrate a specific persuasion technique

    Body:
    {
        "technique": "technique_name",
        "topic": "optional_topic",
        "context": "optional_context"
    }
    """
    try:
        technique_name = request.get("technique", "")
        topic = request.get("topic", "general")
        context = request.get("context", "")

        if not technique_name:
            raise HTTPException(status_code=400, detail="Technique is required")

        # Validate technique
        try:
            technique = PersuasionTechnique(technique_name)
        except ValueError:
            available_techniques = [t.value for t in PersuasionTechnique]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid technique. Available: {available_techniques}"
            )

        # Generate demonstration
        demonstration = meta_persuasion_service.generate_technique_demonstration(
            technique, topic, context
        )

        result = {
            "technique": technique_name,
            "topic": topic,
            "context": context,
            "demonstration": demonstration,
            "educational_value": {
                "technique_explanation": demonstration.get("explanation", ""),
                "real_world_applications": f"This technique is commonly used in {topic} discussions",
                "effectiveness_factors": "Context, audience, and delivery matter significantly"
            },
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"🎭 Technique demonstration generated: {technique_name}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in technique demonstration: {e}")
        raise HTTPException(status_code=500, detail="Demonstration failed")


@app.get("/conversation/{conversation_id}/analysis")
async def get_conversation_analysis_endpoint(conversation_id: str) -> dict:
    """
    Get detailed analysis of a conversation's persuasion patterns
    """
    try:
        if not conversation_id:
            raise HTTPException(status_code=400, detail="Conversation ID is required")

        # Get conversation analysis
        analysis = conversation_service.get_conversation_analysis(conversation_id)

        if not analysis:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Enhance with additional insights
        enhanced_analysis = {
            **analysis,
            "insights": {
                "conversation_flow": "Analyze how persuasion techniques evolved during the conversation",
                "technique_effectiveness": "Evaluate which techniques were most persuasive",
                "learning_opportunities": "Identify areas for improvement in argumentation"
            },
            "recommendations": {
                "for_user": "Consider varying your persuasion techniques for better engagement",
                "for_bot": "Adapt response style based on user's argumentation patterns",
                "educational": "This conversation demonstrates real-world persuasion dynamics"
            },
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"📈 Conversation analysis completed: {conversation_id}")
        return enhanced_analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in conversation analysis: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")


@app.get("/techniques")
async def list_techniques_endpoint() -> dict:
    """
    List all available persuasion techniques with explanations and examples
    """
    try:
        techniques = {}
        for technique in PersuasionTechnique:
            explanation = meta_persuasion_service._explain_technique(technique)

            # Add example usage
            example = meta_persuasion_service._create_technique_example(
                technique, "general", "example context"
            )

            techniques[technique.value] = {
                "name": technique.value,
                "explanation": explanation,
                "example": example,
                "category": _categorize_technique(technique),
                "effectiveness": _rate_technique_effectiveness(technique)
            }

        return {
            "available_techniques": techniques,
            "total_count": len(techniques),
            "categories": {
                "logical": "Techniques based on reasoning and evidence",
                "emotional": "Techniques that appeal to feelings and values",
                "social": "Techniques leveraging social dynamics",
                "structural": "Techniques that organize information effectively"
            },
            "usage_tips": {
                "combination": "Multiple techniques can be combined for greater effect",
                "audience": "Consider your audience when selecting techniques",
                "context": "The situation determines which techniques are most appropriate",
                "ethics": "Use techniques responsibly and transparently"
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error listing techniques: {e}")
        raise HTTPException(status_code=500, detail="Failed to list techniques")


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        redis_status = "connected" if redis_service.is_connected() else "disconnected"
        ai_status = "available" if ai_service.is_available else "fallback"

        health_status = {
            "status": "healthy" if redis_status == "connected" else "degraded",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "redis": {
                    "status": redis_status,
                    "details": redis_service.get_conversation_stats()
                },
                "ai_service": {
                    "status": ai_status,
                    "details": ai_service.get_status()
                },
                "meta_persuasion": {
                    "status": "enabled" if meta_persuasion_service.demonstration_mode else "disabled",
                    "mode": "demonstration" if meta_persuasion_service.demonstration_mode else "passive"
                }
            },
            "version": "2.0.0"
        }

        # Return appropriate HTTP status
        status_code = 200 if health_status["status"] == "healthy" else 503

        if status_code == 503:
            raise HTTPException(status_code=503, detail=health_status)

        return health_status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Health check failed")


@app.get("/stats", response_model=ConversationStats)
async def get_stats():
    """Get system statistics"""
    try:
        redis_stats = redis_service.get_conversation_stats()

        stats = ConversationStats(
            total_conversations=redis_stats.get("conversations", 0),
            redis_status=redis_stats.get("status", "unknown"),
            system_info={
                "ai_service_available": ai_service.is_available,
                "meta_persuasion_enabled": meta_persuasion_service.demonstration_mode,
                "redis_memory": redis_stats.get("redis_info", {}).get("used_memory", "unknown"),
                "version": "2.0.0",
                "uptime": "Since application start"
            }
        )

        logger.info("📊 Stats retrieved successfully")
        return stats

    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


# Helper functions for technique categorization
def _categorize_technique(technique: PersuasionTechnique) -> str:
    """Categorize persuasion techniques"""
    logical_techniques = [
        PersuasionTechnique.LOGICAL_STRUCTURE,
        PersuasionTechnique.ANCHORING,
        PersuasionTechnique.CONTRAST
    ]

    emotional_techniques = [
        PersuasionTechnique.EMOTIONAL_APPEAL,
        PersuasionTechnique.STORYTELLING,
        PersuasionTechnique.SCARCITY
    ]

    social_techniques = [
        PersuasionTechnique.SOCIAL_PROOF,
        PersuasionTechnique.AUTHORITY,
        PersuasionTechnique.BANDWAGON
    ]

    if technique in logical_techniques:
        return "logical"
    elif technique in emotional_techniques:
        return "emotional"
    elif technique in social_techniques:
        return "social"
    else:
        return "structural"


def _rate_technique_effectiveness(technique: PersuasionTechnique) -> str:
    """Rate the general effectiveness of techniques"""
    high_effectiveness = [
        PersuasionTechnique.STORYTELLING,
        PersuasionTechnique.SOCIAL_PROOF,
        PersuasionTechnique.AUTHORITY
    ]

    if technique in high_effectiveness:
        return "high"
    else:
        return "medium"