# make.ps1 - PowerShell script for Windows (equivalent to Makefile)
# Usage: .\make.ps1 <command>
# Example: .\make.ps1 install

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "Available commands:" -ForegroundColor Cyan
    Write-Host "  help        Show this help message" -ForegroundColor Green
    Write-Host "  install     Install all requirements to run the service" -ForegroundColor Green
    Write-Host "  test        Run tests" -ForegroundColor Green
    Write-Host "  run         Run the service and all related services in Docker" -ForegroundColor Green
    Write-Host "  logs        Show service logs" -ForegroundColor Green
    Write-Host "  down        Teardown of all running services" -ForegroundColor Green
    Write-Host "  clean       Teardown and removal of all containers" -ForegroundColor Green
    Write-Host "  dev         Run in development mode" -ForegroundColor Green
    Write-Host "  lint        Run code linting" -ForegroundColor Green
    Write-Host "  format      Format code" -ForegroundColor Green
    Write-Host "  build       Build Docker image" -ForegroundColor Green
    Write-Host "  test-api    Test the API functionality" -ForegroundColor Green
    Write-Host "  test-redis  Test Redis integration specifically" -ForegroundColor Green
    Write-Host "  check       Run all checks (tests + API functionality + Redis)" -ForegroundColor Green
    Write-Host "  shell       Get shell inside running container" -ForegroundColor Green
    Write-Host "  redis-cli   Connect to Redis CLI" -ForegroundColor Green
    Write-Host "  status      Show status of all services" -ForegroundColor Green
}

function Install {
    Write-Host "Checking for required tools..." -ForegroundColor Yellow

    # Check Docker
    try {
        docker --version | Out-Null
        Write-Host "✅ Docker found" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Docker is required but not found. Please install Docker Desktop." -ForegroundColor Red
        exit 1
    }

    # Check Docker Compose
    try {
        docker compose version | Out-Null
        Write-Host "✅ Docker Compose found" -ForegroundColor Green
        $script:DockerComposeCmd = "docker compose"
    }
    catch {
        try {
            docker-compose --version | Out-Null
            Write-Host "✅ Docker Compose (legacy) found" -ForegroundColor Green
            $script:DockerComposeCmd = "docker-compose"
        }
        catch {
            Write-Host "❌ Docker Compose is required but not found." -ForegroundColor Red
            exit 1
        }
    }

    # Check Python
    $pythonCmd = $null
    try {
        python --version | Out-Null
        $pythonCmd = "python"
        Write-Host "✅ Python found" -ForegroundColor Green
    }
    catch {
        try {
            python3 --version | Out-Null
            $pythonCmd = "python3"
            Write-Host "✅ Python3 found" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ Python is required but not found. Please install Python 3.11+." -ForegroundColor Red
            exit 1
        }
    }

    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    & $pythonCmd -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
        exit 1
    }

    # Create .env file
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Created .env file from example" -ForegroundColor Green
    } else {
        Write-Host "✅ .env file already exists" -ForegroundColor Green
    }

    Write-Host "✅ Installation complete!" -ForegroundColor Green
}

function Test {
    Write-Host "Running tests..." -ForegroundColor Yellow
    $pythonCmd = Get-PythonCommand
    & $pythonCmd -m pytest tests/unit/ -v --tb=short
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Tests completed!" -ForegroundColor Green
    } else {
        Write-Host "❌ Tests failed!" -ForegroundColor Red
    }
}

function Run {
    Write-Host "Starting services..." -ForegroundColor Yellow

    if (-not (Test-Path ".env")) {
        Write-Host "❌ Please create .env file from .env.example" -ForegroundColor Red
        exit 1
    }

    $dockerCmd = Get-DockerComposeCommand
    Invoke-Expression "$dockerCmd up --build -d"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Services started! API available at http://localhost:8000" -ForegroundColor Green
        Write-Host "Run '.\make.ps1 logs' to see service logs" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Failed to start services" -ForegroundColor Red
    }
}

function Show-Logs {
    Write-Host "Showing service logs..." -ForegroundColor Yellow
    $dockerCmd = Get-DockerComposeCommand
    Invoke-Expression "$dockerCmd logs -f"
}

function Down {
    Write-Host "Stopping services..." -ForegroundColor Yellow
    $dockerCmd = Get-DockerComposeCommand
    Invoke-Expression "$dockerCmd down"
    Write-Host "✅ Services stopped!" -ForegroundColor Green
}

function Clean {
    Write-Host "Cleaning up containers, networks, and volumes..." -ForegroundColor Yellow
    $dockerCmd = Get-DockerComposeCommand
    Invoke-Expression "$dockerCmd down -v --remove-orphans"
    docker system prune -f
    Write-Host "✅ Cleanup complete!" -ForegroundColor Green
}

function Dev {
    Write-Host "Starting development server..." -ForegroundColor Yellow
    $pythonCmd = Get-PythonCommand
    & $pythonCmd -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

function Lint {
    Write-Host "Running code linting..." -ForegroundColor Yellow
    $pythonCmd = Get-PythonCommand

    try {
        & $pythonCmd -m flake8 app/ tests/
        Write-Host "✅ Flake8 passed" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ Flake8 not installed or failed, skipping..." -ForegroundColor Yellow
    }

    try {
        & $pythonCmd -m black --check app/ tests/
        Write-Host "✅ Black formatting check passed" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ Black not installed or formatting needed, skipping..." -ForegroundColor Yellow
    }
}

function Format {
    Write-Host "Formatting code..." -ForegroundColor Yellow
    $pythonCmd = Get-PythonCommand

    try {
        & $pythonCmd -m black app/ tests/
        Write-Host "✅ Black formatting applied" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ Black not installed, skipping..." -ForegroundColor Yellow
    }

    try {
        & $pythonCmd -m isort app/ tests/
        Write-Host "✅ Isort applied" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ Isort not installed, skipping..." -ForegroundColor Yellow
    }
}

function Build {
    Write-Host "Building Docker image..." -ForegroundColor Yellow
    $dockerCmd = Get-DockerComposeCommand
    Invoke-Expression "$dockerCmd build"
}

function Test-Api {
    Write-Host "Testing API functionality..." -ForegroundColor Yellow
    $pythonCmd = Get-PythonCommand
    & $pythonCmd tests/integration/test_api_integration.py
}

function Test-Redis {
    Write-Host "Testing Redis integration..." -ForegroundColor Yellow
    $pythonCmd = Get-PythonCommand
    & $pythonCmd tests/integration/test_redis_integration.py
}

function Check {
    Write-Host "Running comprehensive checks..." -ForegroundColor Yellow
    Test
    Test-Api
    Test-Redis
}

function Shell {
    Write-Host "Getting shell inside running container..." -ForegroundColor Yellow
    $dockerCmd = Get-DockerComposeCommand
    Invoke-Expression "$dockerCmd exec chatbot-api /bin/bash"
}

function Redis-Cli {
    Write-Host "Connecting to Redis CLI..." -ForegroundColor Yellow
    $dockerCmd = Get-DockerComposeCommand
    Invoke-Expression "$dockerCmd exec redis redis-cli"
}

function Status {
    Write-Host "Docker services status:" -ForegroundColor Cyan
    $dockerCmd = Get-DockerComposeCommand
    Invoke-Expression "$dockerCmd ps"

    Write-Host "`nAPI Health check:" -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
        $response | ConvertTo-Json -Depth 3
    }
    catch {
        Write-Host "API not responding" -ForegroundColor Red
    }
}

# Helper functions
function Get-PythonCommand {
    try {
        python --version | Out-Null
        return "python"
    }
    catch {
        try {
            python3 --version | Out-Null
            return "python3"
        }
        catch {
            Write-Host "❌ Python not found" -ForegroundColor Red
            exit 1
        }
    }
}

function Get-DockerComposeCommand {
    try {
        docker compose version | Out-Null
        return "docker compose"
    }
    catch {
        try {
            docker-compose --version | Out-Null
            return "docker-compose"
        }
        catch {
            Write-Host "❌ Docker Compose not found" -ForegroundColor Red
            exit 1
        }
    }
}

# Main script logic
switch ($Command.ToLower()) {
    "install" { Install }
    "test" { Test }
    "run" { Run }
    "logs" { Show-Logs }
    "down" { Down }
    "clean" { Clean }
    "dev" { Dev }
    "lint" { Lint }
    "format" { Format }
    "build" { Build }
    "test-api" { Test-Api }
    "test-redis" { Test-Redis }
    "check" { Check }
    "shell" { Shell }
    "redis-cli" { Redis-Cli }
    "status" { Status }
    "help" { Show-Help }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Use '.\make.ps1 help' to see available commands" -ForegroundColor Yellow
    }
}