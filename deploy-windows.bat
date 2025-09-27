@echo off
REM Stock Market Analyzer - Windows Batch Deployment Script
REM Simple alternative for users who prefer .bat files

setlocal enabledelayedexpansion

REM Configuration
set PROJECT_NAME=Stock Market Analyzer
set COMPOSE_PROJECT_NAME=stock_market_analyzer

echo.
echo ========================================
echo  %PROJECT_NAME% - Windows Deployment
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed or not in PATH
    echo.
    echo Please install Docker Desktop from:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running
    echo.
    echo Please start Docker Desktop and try again.
    echo.
    pause
    exit /b 1
)

echo ✅ Docker is ready!
echo.

REM Create config file if it doesn't exist
if not exist "config.json" (
    echo Creating default configuration...
    echo { > config.json
    echo   "storage_type": "redis", >> config.json
    echo   "app_mode": "redis", >> config.json
    echo   "redis_host": "redis", >> config.json
    echo   "redis_port": 6379, >> config.json
    echo   "first_run": true >> config.json
    echo } >> config.json
    echo ✅ Configuration created!
)

REM Create credentials directory
if not exist "credentials" (
    mkdir credentials
    echo ✅ Credentials directory created!
)

echo Starting %PROJECT_NAME%...
echo This may take a few minutes on first run...
echo.

REM Start the application
docker compose up -d --build

if %errorlevel% eq 0 (
    echo.
    echo ✅ %PROJECT_NAME% started successfully!
    echo.
    echo 🌐 Access your application at: http://localhost:8501
    echo.
    echo 💡 Useful commands:
    echo    - To stop: docker compose down
    echo    - To view logs: docker compose logs -f
    echo    - To restart: docker compose restart
    echo.
    echo Press any key to open the application in your browser...
    pause >nul
    start http://localhost:8501
) else (
    echo.
    echo ❌ Failed to start %PROJECT_NAME%
    echo.
    echo To see error details, run: docker compose logs
    echo.
    pause
    exit /b 1
)

echo.
echo Thank you for using %PROJECT_NAME%!
pause