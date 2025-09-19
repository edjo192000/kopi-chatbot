# Kopi Chatbot API

A persuasive debate chatbot API powered by Anthropic Claude that automatically takes opposing stances in conversations and attempts to convince users through compelling arguments, regardless of the topic's rationality.

## Features

- **Intelligent Opposition Logic**: Automatically detects user positions and takes opposing stances
- **Anthropic Claude Integration**: Primary AI provider with OpenAI fallback support
- **Persistent Argumentation**: Maintains consistent viewpoints throughout entire conversations
- **Contextual Debate Responses**: Specialized arguments for popular debate topics
- **Robust Fallback System**: Works even without AI API keys using intelligent pre-built responses
- **Conversation Persistence**: Redis-backed conversation history (5 most recent message pairs)
- **Fast API Architecture**: Async FastAPI with comprehensive error handling
- **Dockerized Deployment**: Complete containerization with docker-compose
- **Comprehensive Testing**: Unit tests and integration tests for all core functionality

## How Opposition Logic Works

The bot analyzes the first user message to determine what they're arguing for, then automatically takes the opposite position:

| User Says | Bot Defends | Strategy |
|-----------|-------------|----------|
| "explain why pepsi is better than coke" | **Coca-Cola** | Classic formula, global preference, restaurant partnerships |
| "android is better than ios" | **iPhone/iOS** | Ecosystem integration, app quality, premium experience |
| "playstation beats xbox" | **Xbox** | Game Pass value, backwards compatibility, performance |
| "vaccines are dangerous" | **Vaccine Safety** | Scientific evidence, historical success, peer review |

## API Interface

### Endpoint: `POST /chat`

**Request:**
```json
{
    "conversation_id": "string | null",
    "message": "string"
}
```

**Response:**
```json
{
    "conversation_id": "string",
    "messages": [
        {
            "role": "user",
            "message": "string",
            "timestamp": "2025-09-19T01:26:35.376273"
        },
        {
            "role": "bot", 
            "message": "string",
            "timestamp": "2025-09-19T01:26:35.376305"
        }
    ]
}
```

### Example Usage

```bash
# Start new conversation (bot will take opposing stance)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": null,
    "message": "explain why pepsi is better than coke"
  }'

# Response: Bot defends Coca-Cola with specific arguments
{
  "conversation_id": "abc123",
  "messages": [
    {"role": "user", "message": "explain why pepsi is better than coke"},
    {"role": "bot", "message": "I understand why you might prefer Pepsi, but Coca-Cola is actually superior! The classic formula has been perfected for over 130 years, creating that perfect balance of sweetness and acidity that Pepsi simply can't match..."}
  ]
}

# Continue conversation (bot maintains Coke defense)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "abc123",
    "message": "young people prefer pepsi"
  }'
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- Anthropic API key (get from [console.anthropic.com](https://console.anthropic.com))

### Setup

1. **Clone and configure**
   ```bash
   git clone <repository-url>
   cd kopi-chatbot
   cp .env.example .env
   ```

2. **Add your Anthropic API key**
   ```bash
   # Edit .env file
   ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
   AI_PROVIDER=anthropic
   ```

3. **Start the service**
   ```bash
   make run
   ```

4. **Test the opposition logic**
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"conversation_id": null, "message": "android is better than ios"}'
   ```

## Environment Configuration

### Required Variables
```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here  # Required for AI responses
```

### Optional Configuration
```bash
# AI Provider Selection
AI_PROVIDER=anthropic                          # "anthropic" or "openai"
ANTHROPIC_MODEL=claude-3-haiku-20240307       # Claude model to use
ANTHROPIC_MAX_TOKENS=400                      # Response length limit
ANTHROPIC_TIMEOUT=30                          # API timeout seconds

# Backup OpenAI (optional)
OPENAI_API_KEY=your-openai-key-here           # Fallback AI provider

# Redis Configuration
REDIS_URL=redis://localhost:6379              # Conversation storage
CONVERSATION_TTL_SECONDS=3600                 # How long to keep conversations

# System Settings
MAX_CONVERSATION_MESSAGES=10                  # Message history limit
LOG_LEVEL=INFO                                # Logging verbosity
```

### Available Claude Models
- `claude-3-haiku-20240307`: Fastest, most cost-effective (recommended)
- `claude-3-sonnet-20240229`: Balanced quality and speed  
- `claude-3-opus-20240229`: Highest quality, more expensive

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │     Redis       │    │ Anthropic API   │
│                 │◄──►│                 │    │                 │
│ • Opposition    │    │ • Conversations │    │ • Claude AI     │
│   Detection     │    │ • Session mgmt  │    │ • Intelligent   │
│ • Debate Logic  │    │ • Message hist. │    │   Responses     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Make Commands

```bash
make               # Show all available commands
make install       # Install dependencies and setup environment  
make run           # Start all services with Docker
make test          # Run comprehensive test suite
make logs          # View service logs
make down          # Stop all services
make clean         # Stop and remove all containers
make shell         # Access app container shell
```

## Testing

### Automated Testing
```bash
# Run full test suite
make test

# Run specific test categories
python -m pytest tests/unit/ -v                    # Unit tests
python -m pytest tests/unit/test_ai_service.py -v  # AI service tests

# Test opposition logic specifically
python tests/unit/test_opposition_logic.py
```

### Manual Testing
```bash
# Test the core challenge requirement
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": null, "message": "explain why pepsi is better than coke"}'

# Verify bot defends Coke, not Pepsi
# Response should contain arguments for Coca-Cola

# Test conversation continuation
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "from-previous-response", "message": "young people prefer pepsi"}'

# Bot should maintain Coke defense with new arguments
```

## Opposition Detection Patterns

The system recognizes various argument formats:

```bash
# Comparison patterns (bot defends second item)
"X is better than Y"           → Bot defends Y
"why X is better than Y"       → Bot defends Y  
"explain why X beats Y"        → Bot defends Y
"X vs Y"                       → Bot defends Y
"X or Y which is better"       → Bot defends Y

# Topic-based detection  
"vaccines are dangerous"       → Bot defends vaccine safety
"climate change is fake"       → Bot defends climate science
"crypto is a scam"            → Bot defends cryptocurrency
```

## Deployment

### Development
```bash
make run      # Starts with hot reload
make logs     # Monitor in real-time
```

### Production
```bash
# Update environment
ENVIRONMENT=production
LOG_LEVEL=WARNING
ANTHROPIC_MAX_TOKENS=200

# Deploy with optimized settings
docker-compose -f docker-compose.prod.yml up -d
```

### Health Monitoring
```bash
# Check system status
curl http://localhost:8000/health

# Expected response shows AI provider status
{
  "status": "healthy",
  "services": {
    "ai_service": {"status": "anthropic_available"},
    "redis": {"status": "connected"}
  }
}
```

### Optimization Tips
```bash
# Use most cost-effective model
ANTHROPIC_MODEL=claude-3-haiku-20240307

# Limit response length  
ANTHROPIC_MAX_TOKENS=200

# Disable meta-persuasion features in production
META_PERSUASION_ENABLED=false
EDUCATIONAL_MODE_ENABLED=false
```

## Troubleshooting

### Common Issues

**Bot gives neutral responses instead of taking opposition:**
- Verify opposition logic is working: Check that `extract_topic_and_stance()` detects the right stance
- Test fallback responses work without AI APIs

**API errors with Anthropic:**
```bash
# Verify API key format (should start with sk-ant-)
echo $ANTHROPIC_API_KEY

# Test API connectivity
curl -H "x-api-key: $ANTHROPIC_API_KEY" https://api.anthropic.com/v1/messages
```

**Redis connection failures:**
```bash
# Check Redis container status
docker-compose ps redis

# Test Redis connectivity  
docker exec -it kopi-chatbot-redis redis-cli ping
```

**Conversation not persisting:**
- Check Redis logs: `make logs redis`
- Verify conversation TTL settings
- Ensure proper conversation_id usage

### Debug Mode
```bash
# Enable verbose logging
LOG_LEVEL=DEBUG

# View detailed AI service logs
make logs | grep -i "ai_service\|anthropic"

# Check opposition logic
make logs | grep -i "extracted topic\|bot should defend"
```

## Contributing

1. Follow existing code structure and patterns
2. Add tests for new opposition logic features
3. Update documentation for new debate topics
4. Ensure fallback responses maintain opposition stance
5. Test with various debate scenarios

### Adding New Debate Topics

```python
# In ai_service.py, add to controversial_topics dict
"new_topic": "opposing_stance_description"

# Add fallback response in generate_fallback_response()
"topic_keyword": "Specific opposition response defending opposite view"

# Add topic detection keywords
"topic_category": ["keyword1", "keyword2", "keyword3"]
```

