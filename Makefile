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
	pip install -r requirements.txt
	@echo "Creating .env file from example if it doesn't exist..."
	@test -f .env || cp .env.example .env
	@echo "Installation complete!"

test: ## Run tests
	@echo "Running tests..."
	pytest tests/ -v --tb=short
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
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

lint: ## Run code linting
	@echo "Running linting..."
	flake8 app/ tests/
	black --check app/ tests/

format: ## Format code
	@echo "Formatting code..."
	black app/ tests/
	isort app/ tests/

build: ## Build Docker image
	docker-compose build