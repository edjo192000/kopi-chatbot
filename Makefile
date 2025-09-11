# Makefile for Mac/Linux
.PHONY: help install test run down clean lint format

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install all requirements to run the service
	@echo "Checking for required tools..."
	@command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Please install Docker first."; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || command -v docker compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Please install Docker Compose first."; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Please install Python 3 first."; exit 1; }
	@echo "Installing Python dependencies..."
	pip3 install -r requirements.txt
	@echo "Creating .env file from example if it doesn't exist..."
	@test -f .env || cp .env.example .env
	@echo "Installation complete!"

test: ## Run tests
	@echo "Running tests..."
	python3 -m pytest tests/unit/ -v --tb=short
	@echo "Tests completed!"

run: ## Run the service and all related services in Docker
	@echo "Starting services..."
	@test -f .env || { echo "Please create .env file from .env.example and configure your environment variables"; exit 1; }
	docker-compose up --build -d
	@echo "Services started! API available at http://localhost:8000"
	@echo "Run 'make logs' to see service logs"

logs: ## Show service logs
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
	python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

lint: ## Run code linting
	@echo "Running linting..."
	python3 -m flake8 app/ tests/ || echo "flake8 not installed, skipping..."
	python3 -m black --check app/ tests/ || echo "black not installed, skipping..."

format: ## Format code
	@echo "Formatting code..."
	python3 -m black app/ tests/ || echo "black not installed, skipping..."
	python3 -m isort app/ tests/ || echo "isort not installed, skipping..."

build: ## Build Docker image
	docker-compose build

test-api: ## Test the API functionality
	@echo "Testing API functionality..."
	python3 tests/integration/test_api_integration.py

test-redis: ## Test Redis integration specifically
	@echo "Testing Redis integration..."
	python3 tests/integration/test_redis_integration.py

check: ## Run all checks (tests + API functionality + Redis)
	@echo "Running comprehensive checks..."
	@make test
	@make test-api
	@make test-redis

# Development helpers
shell: ## Get shell inside running container
	docker-compose exec chatbot-api /bin/bash

redis-cli: ## Connect to Redis CLI
	docker-compose exec redis redis-cli

status: ## Show status of all services
	@echo "Docker services status:"
	docker-compose ps
	@echo "\nAPI Health check:"
	@curl -s http://localhost:8000/health | python3 -m json.tool || echo "API not responding"