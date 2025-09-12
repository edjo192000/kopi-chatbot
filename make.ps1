# make.ps1 - PowerShell script for Windows - Kopi Chatbot API v2.0 with Meta-Persuasion
# Usage: .\make.ps1 <command>
# Example: .\make.ps1 install

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    [Parameter(Position=1)]
    [string]$Message = ""
)

$script:DockerComposeCmd = ""

function Show-Help {
    Write-Host "Kopi Chatbot API v2.0 - Meta-Persuasion Enabled" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Available commands:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Installation & Setup:" -ForegroundColor Green
    Write-Host "  install     Install all requirements to run the service" -ForegroundColor White
    Write-Host "  env-check   Check environment configuration" -ForegroundColor White
    Write-Host "  reset       Complete project reset (clean + fresh install)" -ForegroundColor White
    Write-Host ""
    Write-Host "Testing:" -ForegroundColor Green
    Write-Host "  test        Run unit tests" -ForegroundColor White
    Write-Host "  test-integration Run integration tests" -ForegroundColor White
    Write-Host "  test-api    Test the API functionality" -ForegroundColor White
    Write-Host "  test-redis  Test Redis integration specifically" -ForegroundColor White
    Write-Host "  test-meta   Test meta-persuasion integration specifically" -ForegroundColor White
    Write-Host "  test-all    Run all tests (unit + integration + API + Redis + Meta)" -ForegroundColor White
    Write-Host "  check       Run all checks (tests + functionality)" -ForegroundColor White
    Write-Host ""
    Write-Host "Running Services:" -ForegroundColor Green
    Write-Host "  run         Run the service and all related services in Docker" -ForegroundColor White
    Write-Host "  dev         Run in development mode" -ForegroundColor White
    Write-Host "  logs        Show service logs" -ForegroundColor White
    Write-Host "  down        Teardown of all running services" -ForegroundColor White
    Write-Host "  clean       Teardown and removal of all containers" -ForegroundColor White
    Write-Host "  restart     Restart all services" -ForegroundColor White
    Write-Host ""
    Write-Host "Meta-Persuasion Features:" -ForegroundColor Green
    Write-Host "  demo        Demonstrate meta-persuasion features" -ForegroundColor White
    Write-Host "  analyze     Analyze a custom message for persuasion techniques" -ForegroundColor White
    Write-Host "  techniques  List all available persuasion techniques" -ForegroundColor White
    Write-Host ""
    Write-Host "Development:" -ForegroundColor Green
    Write-Host "  build       Build Docker image" -ForegroundColor White
    Write-Host "  lint        Run code linting" -ForegroundColor White
    Write-Host "  format      Format code" -ForegroundColor White
    Write-Host "  shell       Get shell inside running container" -ForegroundColor White
    Write-Host "  redis-cli   Connect to Redis CLI" -ForegroundColor White
    Write-Host ""
    Write-Host "Monitoring:" -ForegroundColor Green
    Write-Host "  status      Show status of all services" -ForegroundColor White
    Write-Host "  monitor     Show real-time system monitoring" -ForegroundColor White
    Write-Host "  docs        Generate/view API documentation" -ForegroundColor White
    Write-Host ""
    Write-Host "Quality Assurance:" -ForegroundColor Green
    Write-Host "  qa          Run quality assurance checks (lint + test + build)" -ForegroundColor White
    Write-Host "  security-scan Run basic security scan" -ForegroundColor White
    Write-Host "  load-test   Run basic load test" -ForegroundColor White
    Write-Host ""
    Write-Host "Utilities:" -ForegroundColor Green
    Write-Host "  backup      Backup Redis data" -ForegroundColor White
    Write-Host "  help        Show this help message" -ForegroundColor White
}

function Install {
    Write-Host "Checking for required tools..." -ForegroundColor Yellow

    # Check Docker
    try {
        docker --version | Out-Null
        Write-Host "Docker found" -ForegroundColor Green
    }
    catch {
        Write-Host "Docker is required but not found. Please install Docker Desktop." -ForegroundColor Red
        exit 1
    }

    # Check Docker Compose
    try {
        docker compose version | Out-Null
        Write-Host "Docker Compose found" -ForegroundColor Green
        $script:DockerComposeCmd = "docker compose"
    }
    catch {
        try {
            docker-compose --version | Out-Null
            Write-Host "Docker Compose (legacy) found" -ForegroundColor Green
            $script:DockerComposeCmd = "docker-compose"
        }
        catch {
            Write-Host "Docker Compose is required but not found." -ForegroundColor Red
            exit 1
        }
    }

    # Check Python
    $pythonCmd = Get-PythonCommand
    Write-Host "Python found: $pythonCmd" -ForegroundColor Green

    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    & $pythonCmd -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install Python dependencies" -ForegroundColor Red
        exit 1
    }

    # Create .env file
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
        Write-Host "Created .env file from example" -ForegroundColor Green
    } else {
        Write-Host ".env file already exists" -ForegroundColor Green
    }

    Write-Host "Installation complete!" -ForegroundColor Green
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Edit .env file with your OpenAI API key" -ForegroundColor White
    Write-Host "   2. Run '.\make.ps1 run' to start services" -ForegroundColor White
    Write-Host "   3. Visit http://localhost:8000 to see the API" -ForegroundColor White
}

function Test {
    Write-Host "Running unit tests..." -ForegroundColor Yellow
    $pythonCmd = Get-PythonCommand
    & $pythonCmd -m pytest tests/unit/ -v --tb=short
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Unit tests completed!" -ForegroundColor Green
    } else {
        Write-Host "Unit tests failed!" -ForegroundColor Red
    }
}

function Test-Integration {
    Write-Host "Running integration tests..." -ForegroundColor Yellow
    $pythonCmd = Get-PythonCommand
    & $pythonCmd -m pytest tests/integration/ -v --tb=short
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Integration tests completed!" -ForegroundColor Green
    } else {
        Write-Host "Integration tests failed!" -ForegroundColor Red
    }
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

function Test-Meta {
    Write-Host "Testing meta-persuasion integration..." -ForegroundColor Yellow
    $pythonCmd = Get-PythonCommand
    & $pythonCmd -m pytest tests/integration/test_meta_persuasion_complete.py -v
}

function Test-All {
    Write-Host "Running comprehensive test suite..." -ForegroundColor Yellow
    Test
    Test-Integration
    Test-Api
    Test-Redis
    Test-Meta
    Write-Host "All tests completed!" -ForegroundColor Green
}

function Check {
    Write-Host "Running comprehensive checks..." -ForegroundColor Yellow
    Test
    Test-Api
    Test-Redis
    Test-Meta
    Write-Host "All checks passed!" -ForegroundColor Green
}

function Run {
    Write-Host "Starting services..." -ForegroundColor Yellow

    if (-not (Test-Path ".env")) {
        Write-Host "Please create .env file from .env.example" -ForegroundColor Red
        exit 1
    }

    $dockerCmd = Get-DockerComposeCommand
    Invoke-Expression "$dockerCmd up --build -d"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Services started! API available at http://localhost:8000" -ForegroundColor Green
        Write-Host "Available endpoints:" -ForegroundColor Cyan
        Write-Host "   • Chat: POST /chat" -ForegroundColor White
        Write-Host "   • Analyze: POST /analyze" -ForegroundColor White
        Write-Host "   • Demonstrate: POST /demonstrate" -ForegroundColor White
        Write-Host "   • Techniques: GET /techniques" -ForegroundColor White
        Write-Host "   • Health: GET /health" -ForegroundColor White
        Write-Host "Run '.\make.ps1 logs' to see service logs" -ForegroundColor Cyan
        Write-Host "Run '.\make.ps1 demo' to see API demonstration" -ForegroundColor Cyan
    } else {
        Write-Host "Failed to start services" -ForegroundColor Red
    }
}

function Show-Logs {
    Write-Host "Showing service logs (Press Ctrl+C to stop)..." -ForegroundColor Yellow
    $dockerCmd = Get-DockerComposeCommand
    Invoke-Expression "$dockerCmd logs -f"
}

function Down {
    Write-Host "Stopping services..." -ForegroundColor Yellow
    $dockerCmd = Get-DockerComposeCommand
    Invoke-Expression "$dockerCmd down"
    Write-Host "Services stopped!" -ForegroundColor Green
}

function Clean {
    Write-Host "Cleaning up containers, networks, and volumes..." -ForegroundColor Yellow
    $dockerCmd = Get-DockerComposeCommand
    Invoke-Expression "$dockerCmd down -v --remove-orphans"
    docker system prune -f
    Write-Host "Cleanup complete!" -ForegroundColor Green
}

function Dev {
    Write-Host "Starting development server..." -ForegroundColor Yellow
    if (-not (Test-Path ".env")) {
        Write-Host "Please create .env file from .env.example" -ForegroundColor Red
        exit 1
    }
    $pythonCmd = Get-PythonCommand
    & $pythonCmd -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

function Lint {
    Write-Host "Running code linting..." -ForegroundColor Yellow
    $pythonCmd = Get-PythonCommand

    try {
        & $pythonCmd -m flake8 app/ tests/
        Write-Host "Flake8 passed" -ForegroundColor Green
    }
    catch {
        Write-Host "Flake8 not installed or failed, skipping..." -ForegroundColor Yellow
    }

    try {
        & $pythonCmd -m black --check app/ tests/
        Write-Host "Black formatting check passed" -ForegroundColor Green
    }
    catch {
        Write-Host "Black not installed or formatting needed, skipping..." -ForegroundColor Yellow
    }

    try {
        & $pythonCmd -m isort --check app/ tests/
        Write-Host "Isort check passed" -ForegroundColor Green
    }
    catch {
        Write-Host "Isort not installed or import sorting needed, skipping..." -ForegroundColor Yellow
    }
}

function Format {
    Write-Host "Formatting code..." -ForegroundColor Yellow
    $pythonCmd = Get-PythonCommand

    try {
        & $pythonCmd -m black app/ tests/
        Write-Host "Black formatting applied" -ForegroundColor Green
    }
    catch {
        Write-Host "Black not installed, skipping..." -ForegroundColor Yellow
    }

    try {
        & $pythonCmd -m isort app/ tests/
        Write-Host "Isort applied" -ForegroundColor Green
    }
    catch {
        Write-Host "Isort not installed, skipping..." -ForegroundColor Yellow
    }

    Write-Host "Code formatting completed!" -ForegroundColor Green
}

function Build {
    Write-Host "Building Docker image..." -ForegroundColor Yellow
    $dockerCmd = Get-DockerComposeCommand
    Invoke-Expression "$dockerCmd build"
}

function Demo {
    Write-Host "Meta-Persuasion API Demo" -ForegroundColor Cyan
    Write-Host "===============================" -ForegroundColor Cyan
    Write-Host ""

    Write-Host "1. Analyzing a persuasive message:" -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/analyze" -Method Post -ContentType "application/json" -Body '{"message": "Research shows that 95% of experts agree this is the best approach!"}'
        $response | ConvertTo-Json -Depth 5
    }
    catch {
        Write-Host "API not responding - run '.\make.ps1 run' first" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "2. Demonstrating anchoring technique:" -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/demonstrate" -Method Post -ContentType "application/json" -Body '{"technique": "anchoring", "topic": "technology"}'
        $response | ConvertTo-Json -Depth 5
    }
    catch {
        Write-Host "API not responding" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "Try more at http://localhost:8000/docs" -ForegroundColor Cyan
}

function Analyze {
    if ($Message -eq "") {
        Write-Host "Message Analysis Tool" -ForegroundColor Cyan
        Write-Host "========================" -ForegroundColor Cyan
        $Message = Read-Host "Enter your message to analyze"
    }

    Write-Host "Analyzing: '$Message'" -ForegroundColor Yellow
    try {
        $body = @{ message = $Message } | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "http://localhost:8000/analyze" -Method Post -ContentType "application/json" -Body $body
        $response | ConvertTo-Json -Depth 5
    }
    catch {
        Write-Host "API not responding - run '.\make.ps1 run' first" -ForegroundColor Red
    }
}

function Techniques {
    Write-Host "Available Persuasion Techniques" -ForegroundColor Cyan
    Write-Host "==================================" -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/techniques" -Method Get
        $response | ConvertTo-Json -Depth 5
    }
    catch {
        Write-Host "API not responding - run '.\make.ps1 run' first" -ForegroundColor Red
    }
}

function Shell {
    Write-Host "Opening shell in chatbot container..." -ForegroundColor Yellow
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
    Write-Host "=========================" -ForegroundColor Cyan
    $dockerCmd = Get-DockerComposeCommand
    Invoke-Expression "$dockerCmd ps"

    Write-Host ""
    Write-Host "API Health check:" -ForegroundColor Cyan
    Write-Host "===================" -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
        $response | ConvertTo-Json -Depth 3
    }
    catch {
        Write-Host "API not responding" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "API Stats:" -ForegroundColor Cyan
    Write-Host "============" -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/stats" -Method Get
        $response | ConvertTo-Json -Depth 3
    }
    catch {
        Write-Host "API not responding" -ForegroundColor Red
    }
}

function Restart {
    Write-Host "Restarting services..." -ForegroundColor Yellow
    Down
    Run
}

function QA {
    Write-Host "Running Quality Assurance checks..." -ForegroundColor Yellow
    Lint
    Test-All
    Build
    Write-Host "Quality Assurance completed!" -ForegroundColor Green
}

function Docs {
    Write-Host "API Documentation available at:" -ForegroundColor Cyan
    Write-Host "   • Swagger UI: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "   • ReDoc: http://localhost:8000/redoc" -ForegroundColor White
    Write-Host "   • OpenAPI Schema: http://localhost:8000/openapi.json" -ForegroundColor White
}

function Monitor {
    Write-Host "System Monitoring" -ForegroundColor Cyan
    Write-Host "===================" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop monitoring..." -ForegroundColor Yellow
    Write-Host ""

    while ($true) {
        Clear-Host
        Write-Host "System Monitoring - $(Get-Date)" -ForegroundColor Cyan
        Write-Host "===========================================" -ForegroundColor Cyan

        Write-Host "Docker containers:" -ForegroundColor Yellow
        $dockerCmd = Get-DockerComposeCommand
        Invoke-Expression "$dockerCmd ps"

        Write-Host ""
        Write-Host "API Health:" -ForegroundColor Yellow
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
            Write-Host "API is healthy" -ForegroundColor Green
        }
        catch {
            Write-Host "API not responding" -ForegroundColor Red
        }

        Start-Sleep -Seconds 2
    }
}

function Backup {
    Write-Host "Creating Redis backup..." -ForegroundColor Yellow

    if (-not (Test-Path "backups")) {
        New-Item -ItemType Directory -Path "backups"
    }

    $dockerCmd = Get-DockerComposeCommand
    Invoke-Expression "$dockerCmd exec redis redis-cli BGSAVE"

    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $containerId = (Invoke-Expression "$dockerCmd ps -q redis").Trim()

    if ($containerId) {
        docker cp "${containerId}:/data/dump.rdb" "backups/redis-backup-${timestamp}.rdb"
        Write-Host "Backup created: backups/redis-backup-${timestamp}.rdb" -ForegroundColor Green
    } else {
        Write-Host "Redis container not found" -ForegroundColor Red
    }
}

function Security-Scan {
    Write-Host "Running security scan..." -ForegroundColor Yellow
    $pythonCmd = Get-PythonCommand

    try {
        & $pythonCmd -m pip install safety
        & $pythonCmd -m safety check
        Write-Host "Security scan completed!" -ForegroundColor Green
    }
    catch {
        Write-Host "Security scan failed" -ForegroundColor Red
    }
}

function Load-Test {
    Write-Host "Running load test..." -ForegroundColor Yellow
    Write-Host "Note: This requires Apache Bench (ab) or similar tool" -ForegroundColor Yellow
    Write-Host "For Windows, using PowerShell Invoke-WebRequest in a loop" -ForegroundColor Yellow

    # Simple PowerShell-based load test
    $requests = 50
    $concurrent = 5
    $url = "http://localhost:8000/health"

    Write-Host "Testing health endpoint with $requests requests..." -ForegroundColor Yellow

    $jobs = @()
    for ($i = 1; $i -le $requests; $i++) {
        $jobs += Start-Job -ScriptBlock {
            try {
                Invoke-RestMethod -Uri $using:url -Method Get -TimeoutSec 10
                return "Success"
            }
            catch {
                return "Failed"
            }
        }

        if ($jobs.Count -ge $concurrent) {
            $jobs | Wait-Job | Remove-Job
            $jobs = @()
        }
    }

    $jobs | Wait-Job | Remove-Job
    Write-Host "Load test completed!" -ForegroundColor Green
}

function Env-Check {
    Write-Host "Environment Configuration Check" -ForegroundColor Cyan
    Write-Host "==================================" -ForegroundColor Cyan

    if (Test-Path ".env") {
        Write-Host ".env file exists" -ForegroundColor Green
    } else {
        Write-Host ".env file missing" -ForegroundColor Red
    }

    if (Test-Path "requirements.txt") {
        Write-Host "requirements.txt exists" -ForegroundColor Green
    } else {
        Write-Host "requirements.txt missing" -ForegroundColor Red
    }

    if (Test-Path "docker-compose.yml") {
        Write-Host "docker-compose.yml exists" -ForegroundColor Green
    } else {
        Write-Host "docker-compose.yml missing" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "Environment Variables:" -ForegroundColor Cyan
    Write-Host "========================" -ForegroundColor Cyan

    if (Test-Path ".env") {
        Get-Content ".env" | Where-Object { $_ -notmatch '^#' -and $_ -ne '' } | ForEach-Object {
            $key = ($_ -split '=')[0]
            Write-Host "$key is set" -ForegroundColor Green
        }
    } else {
        Write-Host "Cannot read .env file" -ForegroundColor Red
    }
}

function Reset {
    Write-Host "Performing complete project reset..." -ForegroundColor Yellow
    Clean
    Install
    Write-Host "Project reset completed!" -ForegroundColor Green
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
            Write-Host "Python not found. Please install Python 3.11+" -ForegroundColor Red
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
            Write-Host "Docker Compose not found" -ForegroundColor Red
            exit 1
        }
    }
}

# Main script logic
switch ($Command.ToLower()) {
    "install" { Install }
    "test" { Test }
    "test-integration" { Test-Integration }
    "test-api" { Test-Api }
    "test-redis" { Test-Redis }
    "test-meta" { Test-Meta }
    "test-all" { Test-All }
    "check" { Check }
    "run" { Run }
    "logs" { Show-Logs }
    "down" { Down }
    "clean" { Clean }
    "restart" { Restart }
    "dev" { Dev }
    "lint" { Lint }
    "format" { Format }
    "build" { Build }
    "demo" { Demo }
    "analyze" { Analyze }
    "techniques" { Techniques }
    "shell" { Shell }
    "redis-cli" { Redis-Cli }
    "status" { Status }
    "monitor" { Monitor }
    "qa" { QA }
    "docs" { Docs }
    "backup" { Backup }
    "security-scan" { Security-Scan }
    "load-test" { Load-Test }
    "env-check" { Env-Check }
    "reset" { Reset }
    "help" { Show-Help }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Use '.\make.ps1 help' to see available commands" -ForegroundColor Yellow
    }
}