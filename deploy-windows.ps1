# Stock Market Analyzer - Windows Deployment Script
# This script automates the setup and deployment of the Stock Market Analyzer on Windows

param(
    [string]$Action = "start",
    [switch]$Help,
    [switch]$Cleanup,
    [switch]$Update,
    [switch]$Logs,
    [switch]$Status
)

# Script configuration
$SCRIPT_NAME = "Stock Market Analyzer Deployment"
$PROJECT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$DOCKER_COMPOSE_FILE = Join-Path $PROJECT_DIR "docker-compose.yml"
$CONFIG_FILE = Join-Path $PROJECT_DIR "config.json"

# Colors for output
$RED = "Red"
$GREEN = "Green"
$YELLOW = "Yellow"
$BLUE = "Cyan"
$MAGENTA = "Magenta"

function Write-Header {
    param([string]$Message)
    Write-Host "========================================" -ForegroundColor $BLUE
    Write-Host " $Message" -ForegroundColor $BLUE
    Write-Host "========================================" -ForegroundColor $BLUE
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $GREEN
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $RED
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $YELLOW
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor $BLUE
}

function Show-Help {
    Write-Header "Stock Market Analyzer - Help"
    Write-Host ""
    Write-Host "USAGE:" -ForegroundColor $YELLOW
    Write-Host "  .\deploy-windows.ps1 [ACTION] [OPTIONS]" -ForegroundColor $WHITE
    Write-Host ""
    Write-Host "ACTIONS:" -ForegroundColor $YELLOW
    Write-Host "  start     Start the application (default)" -ForegroundColor $WHITE
    Write-Host "  stop      Stop the application" -ForegroundColor $WHITE
    Write-Host "  restart   Restart the application" -ForegroundColor $WHITE
    Write-Host "  build     Build/rebuild the application" -ForegroundColor $WHITE
    Write-Host ""
    Write-Host "OPTIONS:" -ForegroundColor $YELLOW
    Write-Host "  -Help     Show this help message" -ForegroundColor $WHITE
    Write-Host "  -Cleanup  Remove all containers and volumes (WARNING: Data loss!)" -ForegroundColor $WHITE
    Write-Host "  -Update   Pull latest images and rebuild" -ForegroundColor $WHITE
    Write-Host "  -Logs     Show application logs" -ForegroundColor $WHITE
    Write-Host "  -Status   Show current status" -ForegroundColor $WHITE
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor $YELLOW
    Write-Host "  .\deploy-windows.ps1                    # Start the application" -ForegroundColor $WHITE
    Write-Host "  .\deploy-windows.ps1 start              # Start the application" -ForegroundColor $WHITE
    Write-Host "  .\deploy-windows.ps1 stop               # Stop the application" -ForegroundColor $WHITE
    Write-Host "  .\deploy-windows.ps1 build              # Build and start" -ForegroundColor $WHITE
    Write-Host "  .\deploy-windows.ps1 -Logs              # Show logs" -ForegroundColor $WHITE
    Write-Host "  .\deploy-windows.ps1 -Status            # Check status" -ForegroundColor $WHITE
    Write-Host ""
    Write-Host "ACCESS:" -ForegroundColor $YELLOW
    Write-Host "  Once started, access the application at: http://localhost:8501" -ForegroundColor $GREEN
    Write-Host ""
}

function Test-DockerInstalled {
    try {
        $dockerVersion = docker --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
    }
    catch {
        return $false
    }
    return $false
}

function Test-DockerRunning {
    try {
        docker info 2>$null | Out-Null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

function Test-DockerCompose {
    try {
        docker compose version 2>$null | Out-Null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

function Initialize-Config {
    Write-Info "Initializing configuration..."

    # Check for Google Sheets setup
    $hasGoogleCreds = (Test-Path "credentials\service.json") -or (Test-Path "credentials\google_credentials.json")

    if (-not (Test-Path $CONFIG_FILE)) {
        # Determine default storage type based on available credentials
        $storageType = if ($hasGoogleCreds) { "google_sheets" } else { "redis" }

        $defaultConfig = @{
            storage_type = $storageType
            app_mode = $storageType
            redis_host = "redis"
            redis_port = 6379
            first_run = $true
            created_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        }

        # Add Google Sheets config if credentials exist
        if ($hasGoogleCreds) {
            $defaultConfig.google_credentials_file = "/app/credentials/google_credentials.json"
            # Try to read existing sheet ID from any previous config
            $defaultConfig.google_sheet_id = ""
            Write-Info "Google credentials detected - configuring for Google Sheets storage"
        }

        $defaultConfig | ConvertTo-Json -Depth 10 | Set-Content $CONFIG_FILE -Encoding UTF8
        Write-Success "Created configuration file for $storageType storage"
    } else {
        Write-Info "Configuration file already exists"

        # Auto-upgrade existing config if Google credentials are available
        if ($hasGoogleCreds) {
            try {
                $existingConfig = Get-Content $CONFIG_FILE | ConvertFrom-Json
                if ($existingConfig.storage_type -eq "redis" -and -not $existingConfig.google_credentials_file) {
                    Write-Info "Google credentials found - would you like to switch to Google Sheets?"
                    Write-Host "Run '.\setup-google-sheets.ps1' to configure Google Sheets storage" -ForegroundColor $YELLOW
                }
            } catch {
                Write-Warning "Could not read existing configuration"
            }
        }
    }

    # Ensure credentials directory exists
    if (-not (Test-Path "credentials")) {
        New-Item -ItemType Directory -Path "credentials" -Force | Out-Null
        Write-Success "Created credentials directory"
    }

    # Copy service.json to expected filename if needed
    if ((Test-Path "credentials\service.json") -and -not (Test-Path "credentials\google_credentials.json")) {
        Copy-Item "credentials\service.json" "credentials\google_credentials.json" -Force
        Write-Info "Prepared Google credentials for Docker"
    }
}

function Test-Prerequisites {
    Write-Header "Checking Prerequisites"

    $allGood = $true

    # Check Docker installation
    Write-Host "Checking Docker installation..." -NoNewline
    if (Test-DockerInstalled) {
        Write-Host " ✅" -ForegroundColor $GREEN
        $dockerVersion = docker --version
        Write-Info "Found: $dockerVersion"
    } else {
        Write-Host " ❌" -ForegroundColor $RED
        Write-Error "Docker is not installed or not in PATH"
        Write-Warning "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
        $allGood = $false
    }

    # Check Docker running
    if ($allGood) {
        Write-Host "Checking Docker service..." -NoNewline
        if (Test-DockerRunning) {
            Write-Host " ✅" -ForegroundColor $GREEN
        } else {
            Write-Host " ❌" -ForegroundColor $RED
            Write-Error "Docker is not running"
            Write-Warning "Please start Docker Desktop"
            $allGood = $false
        }
    }

    # Check Docker Compose
    if ($allGood) {
        Write-Host "Checking Docker Compose..." -NoNewline
        if (Test-DockerCompose) {
            Write-Host " ✅" -ForegroundColor $GREEN
            $composeVersion = docker compose version
            Write-Info "Found: $composeVersion"
        } else {
            Write-Host " ❌" -ForegroundColor $RED
            Write-Error "Docker Compose is not available"
            Write-Warning "Please ensure you have Docker Desktop with Compose support"
            $allGood = $false
        }
    }

    # Check docker-compose.yml
    Write-Host "Checking docker-compose.yml..." -NoNewline
    if (Test-Path $DOCKER_COMPOSE_FILE) {
        Write-Host " ✅" -ForegroundColor $GREEN
    } else {
        Write-Host " ❌" -ForegroundColor $RED
        Write-Error "docker-compose.yml not found in project directory"
        $allGood = $false
    }

    if (-not $allGood) {
        Write-Error "Prerequisites check failed. Please fix the issues above and try again."
        exit 1
    }

    Write-Success "All prerequisites met!"
    return $true
}

function Get-ContainerStatus {
    try {
        $status = docker compose ps --format json 2>$null | ConvertFrom-Json
        return $status
    }
    catch {
        return @()
    }
}

function Show-Status {
    Write-Header "Application Status"

    $containers = Get-ContainerStatus

    if ($containers.Count -eq 0) {
        Write-Warning "No containers are running"
        Write-Info "Use '.\deploy-windows.ps1 start' to start the application"
        return
    }

    foreach ($container in $containers) {
        $serviceName = $container.Service
        $state = $container.State
        $status = $container.Status

        $statusColor = switch ($state) {
            "running" { $GREEN }
            "exited" { $RED }
            "paused" { $YELLOW }
            default { $YELLOW }
        }

        Write-Host "Service: $serviceName" -ForegroundColor $BLUE
        Write-Host "  State: $state" -ForegroundColor $statusColor
        Write-Host "  Status: $status" -ForegroundColor $WHITE

        if ($serviceName -eq "app" -and $state -eq "running") {
            Write-Host "  URL: http://localhost:8501" -ForegroundColor $GREEN
        }
        Write-Host ""
    }

    # Show volume information
    Write-Info "Data Volumes:"
    try {
        $volumes = docker volume ls --filter "name=stock_market_analyzer" --format "{{.Name}}" 2>$null
        foreach ($volume in $volumes) {
            if ($volume) {
                Write-Host "  📁 $volume" -ForegroundColor $BLUE
            }
        }
    }
    catch {
        Write-Warning "Could not retrieve volume information"
    }
}

function Start-Application {
    param([bool]$Build = $false)

    Write-Header "Starting Stock Market Analyzer"

    Initialize-Config

    # Check if Google Sheets setup is incomplete
    $hasGoogleCreds = (Test-Path "credentials\service.json") -or (Test-Path "credentials\google_credentials.json")
    if ($hasGoogleCreds) {
        try {
            $config = Get-Content $CONFIG_FILE | ConvertFrom-Json
            if ($config.storage_type -eq "google_sheets" -and (-not $config.google_sheet_id -or $config.google_sheet_id -eq "")) {
                Write-Warning "Google credentials found but Google Sheets ID is missing!"
                Write-Host ""
                Write-Host "To complete Google Sheets setup, run:" -ForegroundColor $YELLOW
                Write-Host ".\setup-google-sheets.ps1" -ForegroundColor $GREEN
                Write-Host ""
                $continue = Read-Host "Continue with current setup? (Y/n)"
                if ($continue.ToLower() -eq "n") {
                    Write-Info "Setup cancelled. Run the Google Sheets setup wizard first."
                    return
                }
            }
        } catch {
            Write-Warning "Could not validate Google Sheets configuration"
        }
    }

    if ($Build) {
        Write-Info "Building and starting application..."
        docker compose up -d --build
    } else {
        Write-Info "Starting application..."
        docker compose up -d
    }

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Application started successfully!"
        Write-Host ""

        # Show storage type
        try {
            $config = Get-Content $CONFIG_FILE | ConvertFrom-Json
            $storageDisplay = if ($config.storage_type -eq "google_sheets") { "📈 Google Sheets" } else { "🗄️ Redis Database" }
            Write-Info "Storage: $storageDisplay"
        } catch {
            Write-Info "Storage: Default configuration"
        }

        Write-Host ""
        Write-Host "🌐 Access your application at: " -NoNewline -ForegroundColor $BLUE
        Write-Host "http://localhost:8501" -ForegroundColor $GREEN
        Write-Host ""
        Write-Info "Use '.\deploy-windows.ps1 -Logs' to view application logs"
        Write-Info "Use '.\deploy-windows.ps1 -Status' to check container status"

        # Show Google Sheets setup reminder if applicable
        if ($hasGoogleCreds) {
            Write-Host ""
            Write-Info "💡 Tip: Use '.\setup-google-sheets.ps1' to configure Google Sheets"
        }

        # Wait a moment and check if containers are healthy
        Write-Info "Waiting for services to start..."
        Start-Sleep -Seconds 5
        Show-Status
    } else {
        Write-Error "Failed to start application"
        Write-Info "Use '.\deploy-windows.ps1 -Logs' to see error details"
        exit 1
    }
}

function Stop-Application {
    Write-Header "Stopping Stock Market Analyzer"

    Write-Info "Stopping application..."
    docker compose down

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Application stopped successfully!"
    } else {
        Write-Error "Failed to stop application"
        exit 1
    }
}

function Restart-Application {
    Write-Header "Restarting Stock Market Analyzer"

    Stop-Application
    Start-Sleep -Seconds 2
    Start-Application
}

function Show-Logs {
    Write-Header "Application Logs"

    Write-Info "Showing logs (Press Ctrl+C to stop)..."
    Write-Host ""

    try {
        docker compose logs -f
    }
    catch {
        Write-Warning "Log viewing interrupted"
    }
}

function Update-Application {
    Write-Header "Updating Stock Market Analyzer"

    Write-Info "Pulling latest images..."
    docker compose pull

    Write-Info "Rebuilding and restarting..."
    docker compose up -d --build

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Application updated successfully!"
        Start-Sleep -Seconds 5
        Show-Status
    } else {
        Write-Error "Update failed"
        exit 1
    }
}

function Cleanup-Application {
    Write-Header "Cleanup Stock Market Analyzer"

    Write-Warning "This will remove ALL containers, images, and volumes."
    Write-Warning "ALL YOUR DATA WILL BE LOST!"
    Write-Host ""

    $confirmation = Read-Host "Type 'DELETE ALL DATA' to confirm"

    if ($confirmation -eq "DELETE ALL DATA") {
        Write-Info "Stopping containers..."
        docker compose down

        Write-Info "Removing containers and volumes..."
        docker compose down -v --remove-orphans

        Write-Info "Removing project images..."
        docker image rm stock_market_analyzer-app 2>$null

        Write-Success "Cleanup completed!"
    } else {
        Write-Info "Cleanup cancelled"
    }
}

function Open-Browser {
    try {
        Start-Process "http://localhost:8501"
        Write-Success "Opening application in default browser..."
    }
    catch {
        Write-Info "Could not automatically open browser. Please navigate to: http://localhost:8501"
    }
}

# Main script execution
try {
    # Show help if requested
    if ($Help) {
        Show-Help
        exit 0
    }

    # Handle flag-based actions
    if ($Status) {
        Test-Prerequisites | Out-Null
        Show-Status
        exit 0
    }

    if ($Logs) {
        Test-Prerequisites | Out-Null
        Show-Logs
        exit 0
    }

    if ($Cleanup) {
        Test-Prerequisites | Out-Null
        Cleanup-Application
        exit 0
    }

    if ($Update) {
        Test-Prerequisites | Out-Null
        Update-Application
        exit 0
    }

    # Test prerequisites for main actions
    Test-Prerequisites | Out-Null

    # Handle main actions
    switch ($Action.ToLower()) {
        "start" {
            Start-Application
        }
        "stop" {
            Stop-Application
        }
        "restart" {
            Restart-Application
        }
        "build" {
            Start-Application -Build $true
        }
        "status" {
            Show-Status
        }
        "logs" {
            Show-Logs
        }
        default {
            Write-Error "Unknown action: $Action"
            Write-Info "Use '.\deploy-windows.ps1 -Help' for usage information"
            exit 1
        }
    }
}
catch {
    Write-Error "An unexpected error occurred: $($_.Exception.Message)"
    Write-Info "Please check the error details above and try again"
    exit 1
}