# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Literal
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Kopi Chatbot API",
    description="API for a persuasive chatbot that can hold debates",
    version="1.0.0"
)


# Pydantic models
class Message(BaseModel):
    role: Literal["user", "bot"]
    message: str


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    conversation_id: str
    messages: List[Message]


# In-memory storage for now (will be replaced with Redis)
conversations = {}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Kopi Chatbot API is running"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    """
    try:
        # Generate or use existing conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # Get or initialize conversation
        if conversation_id not in conversations:
            conversations[conversation_id] = []

        # Add user message to conversation
        user_message = Message(role="user", message=request.message)
        conversations[conversation_id].append(user_message)

        # TODO: Generate bot response using AI service
        # For now, simple placeholder response
        bot_response = await generate_bot_response(
            conversation_id,
            conversations[conversation_id]
        )

        bot_message = Message(role="bot", message=bot_response)
        conversations[conversation_id].append(bot_message)

        # Keep only last 10 messages (5 pairs) to maintain the 5 most recent
        conversations[conversation_id] = conversations[conversation_id][-10:]

        return ChatResponse(
            conversation_id=conversation_id,
            messages=conversations[conversation_id]
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def generate_bot_response(conversation_id: str, messages: List[Message]) -> str:
    """
    Generate bot response based on conversation history
    TODO: Implement AI-powered response generation
    """
    if len(messages) == 1:  # First message - establish position
        user_msg = messages[0].message.lower()

        # Simple topic detection and position taking
        if "flat earth" in user_msg or "earth" in user_msg:
            return "I absolutely believe the Earth is flat! The evidence is all around us - when you look at the horizon, it appears completely flat. NASA and other space agencies have been deceiving us for decades with their fake images and CGI. Have you ever seen a real photograph of Earth that wasn't manipulated?"

        elif "vaccine" in user_msg:
            return "Vaccines are one of the greatest medical achievements in human history! They have eradicated diseases like smallpox and nearly eliminated polio. The scientific evidence overwhelmingly shows they are safe and effective. The few side effects are minimal compared to the devastating diseases they prevent."

        else:
            # Default persuasive response
            return f"That's an interesting topic you've brought up. Let me share why I have strong convictions about this matter and why I believe my perspective is the correct one..."

    else:
        # Continue the debate - maintain position
        return "I understand your point, but I still firmly believe in my position. Let me explain why the evidence supports my view..."


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)