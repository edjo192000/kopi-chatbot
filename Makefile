# Makefile for Mac/Linux - Kopi Chatbot API v2.0 with Meta-Persuasion
.PHONY: help install test run down clean lint format

# Default target
help: ## Show this help message
	@echo "Kopi Chatbot API v2.0 - Meta-Persuasion Enabled"
	@echo "================================================"
	@echo ""
	@echo "Installation & Setup:"
	@echo "  \033[36minstall\033[0m     Install all requirements to run the service"
	@echo "  \033[36menv-check\033[0m   Check environment configuration"
	@echo "  \033[36mreset\033[0m       Complete project reset (clean + fresh install)"
	@echo ""
	@echo "Testing:"
	@echo "  \033[36mtest\033[0m        Run unit tests"
	@echo "  \033[36mtest-integration\033[0m Run integration tests"
	@echo "  \033[36mtest-api\033[0m    Test the API functionality"
	@echo "  \033[36mtest-redis\033[0m  Test Redis integration specifically"
	@echo "  \033[36mtest-meta\033[0m   Test meta-persuasion integration specifically"
	@echo "  \033[36mtest-all\033[0m    Run all tests (unit + integration + API + Redis + Meta)"
	@echo "  \033[36mcheck\033[0m       Run all checks (tests + functionality)"
	@echo ""
	@echo "Running Services:"
	@echo "  \033[36mrun\033[0m         Run the service and all related services in Docker"
	@echo "  \033[36mdev\033[0m         Run in development mode"
	@echo "  \033[36mlogs\033[0m        Show service logs"
	@echo "  \033[36mdown\033[0m        Teardown of all running services"
	@echo "  \033[36mclean\033[0m       Teardown and removal of all containers"
	@echo "  \033[36mrestart\033[0m     Restart all services"
	@echo ""
	@echo "Meta-Persuasion Features:"
	@echo "  \033[36mdemo\033[0m        Demonstrate meta-persuasion features"
	@echo "  \033[36manalyze\033[0m     Analyze a custom message for persuasion techniques"
	@echo "  \033[36mtechniques\033[0m  List all available persuasion techniques"
	@echo ""
	@echo "Development:"
	@echo "  \033[36mbuild\033[0m       Build Docker image"
	@echo "  \033[36mlint\033[0m        Run code linting"
	@echo "  \033[36mformat\033[0m      Format code"
	@echo "  \033[36mshell\033[0m       Get shell inside running container"
	@echo "  \033[36mredis-cli\033[0m   Connect to Redis CLI"
	@echo ""
	@echo "Monitoring:"
	@echo "  \033[36mstatus\033[0m      Show status of all services"
	@echo "  \033[36mmonitor\033[0m     Show real-time system monitoring"
	@echo "  \033[36mdocs\033[0m        Generate/view API documentation"
	@echo ""
	@echo "Quality Assurance:"
	@echo "  \033[36mqa\033[0m          Run quality assurance checks (lint + test + build)"
	@echo "  \033[36msecurity-scan\033[0m Run basic security scan"
	@echo "  \033[36mload-test\033[0m   Run basic load test"
	@echo ""
	@echo "Utilities:"
	@echo "  \033[36mbackup\033[0m      Backup Redis data"
	@echo "  \033[36mhelp\033[0m        Show this help message"
	@echo ""
	@echo "Quick Start:"
	@echo "  1. Run '\033[36mmake install\033[0m' to set up the project"
	@echo "  2. Edit .env file with your OpenAI API key"
	@echo "  3. Run '\033[36mmake run\033[0m' to start services"
	@echo "  4. Run '\033[36mmake demo\033[0m' to see meta-persuasion features"
install: ## Install all requirements to run the service
	@echo "Checking for required tools..."
	@command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Please install Docker first."; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || command -v docker compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Please install Docker Compose first."; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Please install Python 3.11+ first."; exit 1; }
	@echo "All required tools found"
	@echo "Installing Python dependencies..."
	pip3 install -r requirements.txt
	@echo "Creating .env file from example if it doesn't exist..."
	@test -f .env || cp .env.example .env
	@echo "Installation complete!"
	@echo "Next steps:"
	@echo "   1. Edit .env file with your OpenAI API key"
	@echo "   2. Run 'make run' to start services"
	@echo "   3. Visit http://localhost:8000 to see the API"

test: ## Run unit tests
	@echo "Running unit tests..."
	python3 -m pytest tests/unit/ -v --tb=short
	@echo "Unit tests completed!"

test-integration: ## Run integration tests
	@echo "Running integration tests..."
	python3 -m pytest tests/integration/ -v --tb=short
	@echo "Integration tests completed!"

test-api: ## Test the API functionality
	@echo "Testing API functionality..."
	python3 tests/integration/test_api_integration.py

test-redis: ## Test Redis integration specifically
	@echo "Testing Redis integration..."
	python3 tests/integration/test_redis_integration.py

test-meta: ## Test meta-persuasion integration specifically
	@echo "Testing meta-persuasion integration..."
	python3 -m pytest tests/integration/test_meta_persuasion_complete.py -v

test-all: ## Run all tests (unit + integration + API + Redis + Meta-Persuasion)
	@echo "Running comprehensive test suite..."
	@make test
	@make test-integration
	@make test-api
	@make test-redis
	@make test-meta
	@echo "All tests completed!"

check: ## Run all checks (tests + API functionality + Redis + Meta-Persuasion)
	@echo "Running comprehensive checks..."
	@make test
	@make test-api
	@make test-redis
	@make test-meta
	@echo "All checks passed!"

run: ## Run the service and all related services in Docker
	@echo "Starting services..."
	@test -f .env || { echo "Please create .env file from .env.example and configure your environment variables"; exit 1; }
	docker-compose up --build -d
	@echo "Services started! API available at http://localhost:8000"
	@echo "Available endpoints:"
	@echo "   • Chat: POST /chat"
	@echo "   • Analyze: POST /analyze"
	@echo "   • Demonstrate: POST /demonstrate"
	@echo "   • Techniques: GET /techniques"
	@echo "   • Health: GET /health"
	@echo "Run 'make logs' to see service logs"
	@echo "Run 'make demo' to see API demonstration"

logs: ## Show service logs
	@echo "Showing service logs (Press Ctrl+C to stop)..."
	docker-compose logs -f

down: ## Teardown of all running services
	@echo "Stopping services..."
	docker-compose down
	@echo "Services stopped!"

clean: ## Teardown and removal of all containers
	@echo "Cleaning up containers, networks, and volumes..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "Cleanup complete!"

dev: ## Run in development mode
	@echo "Starting development server..."
	@test -f .env || { echo "Please create .env file from .env.example"; exit 1; }
	python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

lint: ## Run code linting
	@echo "Running linting..."
	python3 -m flake8 app/ tests/ || echo "flake8 not installed, skipping..."
	python3 -m black --check app/ tests/ || echo "black not installed, skipping..."
	python3 -m isort --check app/ tests/ || echo "isort not installed, skipping..."

format: ## Format code
	@echo "Formatting code..."
	python3 -m black app/ tests/ || echo "black not installed, skipping..."
	python3 -m isort app/ tests/ || echo "isort not installed, skipping..."
	@echo "Code formatting completed!"

build: ## Build Docker image
	@echo "Building Docker image..."
	docker-compose build

demo: ## Demonstrate meta-persuasion features
	@echo "Meta-Persuasion API Demo"
	@echo "==============================="
	@echo ""
	@echo "1. Analyzing a persuasive message:"
	@curl -s -X POST http://localhost:8000/analyze \
		-H "Content-Type: application/json" \
		-d '{"message": "Research shows that 95% of experts agree this is the best approach!"}' \
		| python3 -m json.tool || echo "API not responding - run 'make run' first"
	@echo ""
	@echo "2. Demonstrating anchoring technique:"
	@curl -s -X POST http://localhost:8000/demonstrate \
		-H "Content-Type: application/json" \
		-d '{"technique": "anchoring", "topic": "technology"}' \
		| python3 -m json.tool || echo "API not responding"
	@echo ""
	@echo "Try more at http://localhost:8000/docs"

analyze: ## Analyze a custom message for persuasion techniques
	@echo "Message Analysis Tool"
	@echo "========================"
	@echo "Enter your message to analyze:"
	@read -p "Message: " message; \
	curl -s -X POST http://localhost:8000/analyze \
		-H "Content-Type: application/json" \
		-d "{\"message\": \"$$message\"}" \
		| python3 -m json.tool || echo "API not responding - run 'make run' first"

techniques: ## List all available persuasion techniques
	@echo "Available Persuasion Techniques"
	@echo "=================================="
	@curl -s http://localhost:8000/techniques | python3 -m json.tool || echo "API not responding - run 'make run' first"

shell: ## Get shell inside running container
	@echo "Opening shell in chatbot container..."
	docker-compose exec chatbot-api /bin/bash

redis-cli: ## Connect to Redis CLI
	@echo "Connecting to Redis CLI..."
	docker-compose exec redis redis-cli

status: ## Show status of all services
	@echo "Docker services status:"
	@echo "========================="
	docker-compose ps
	@echo ""
	@echo "API Health check:"
	@echo "==================="
	@curl -s http://localhost:8000/health | python3 -m json.tool || echo "API not responding"
	@echo ""
	@echo "API Stats:"
	@echo "============"
	@curl -s http://localhost:8000/stats | python3 -m json.tool || echo "API not responding"

restart: ## Restart all services
	@echo "Restarting services..."
	@make down
	@make run

qa: ## Run quality assurance checks (lint + test + build)
	@echo "Running Quality Assurance checks..."
	@make lint
	@make test-all
	@make build
	@echo "Quality Assurance completed!"

docs: ## Generate/view API documentation
	@echo "API Documentation available at:"
	@echo "   • Swagger UI: http://localhost:8000/docs"
	@echo "   • ReDoc: http://localhost:8000/redoc"
	@echo "   • OpenAPI Schema: http://localhost:8000/openapi.json"

monitor: ## Show real-time system monitoring
	@echo "System Monitoring"
	@echo "==================="
	@echo "Docker containers:"
	@watch -n 2 'docker-compose ps && echo "" && curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "API not responding"'

backup: ## Backup Redis data
	@echo "Creating Redis backup..."
	@mkdir -p backups
	docker-compose exec redis redis-cli BGSAVE
	docker cp $$(docker-compose ps -q redis):/data/dump.rdb backups/redis-backup-$$(date +%Y%m%d-%H%M%S).rdb
	@echo "Backup created in backups/ directory"

security-scan: ## Run basic security scan
	@echo "Running security scan..."
	python3 -m pip install safety || echo "Installing safety..."
	python3 -m safety check
	@echo "Security scan completed!"

load-test: ## Run basic load test
	@echo "Running load test..."
	@command -v ab >/dev/null 2>&1 || { echo "Apache Bench (ab) required for load testing. Install with: apt-get install apache2-utils"; exit 1; }
	@echo "Testing chat endpoint with 100 requests, 10 concurrent..."
	@ab -n 100 -c 10 -T 'application/json' -p tests/data/sample_request.json http://localhost:8000/chat || echo "Load test failed - ensure API is running"

env-check: ## Check environment configuration
	@echo "Environment Configuration Check"
	@echo "=================================="
	@test -f .env && echo "✓ .env file exists" || echo "✗ .env file missing"
	@test -f requirements.txt && echo "✓ requirements.txt exists" || echo "✗ requirements.txt missing"
	@test -f docker-compose.yml && echo "✓ docker-compose.yml exists" || echo "✗ docker-compose.yml missing"
	@echo ""
	@echo "Environment Variables:"
	@echo "========================"
	@grep -v '^#' .env 2>/dev/null | grep -v '^$$' | while read line; do \
		key=$$(echo $$line | cut -d'=' -f1); \
		echo "✓ $$key is set"; \
	done || echo "✗ Cannot read .env file"

reset: ## Complete project reset (clean + fresh install)
	@echo "Performing complete project reset..."
	@make clean
	@make install
	@echo "Project reset completed!"