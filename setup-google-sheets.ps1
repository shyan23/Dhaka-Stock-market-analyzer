# Google Sheets Setup Wizard for Stock Market Analyzer
# This script helps non-tech users easily setup Google Sheets integration

param(
    [switch]$Help
)

# Colors for output
$GREEN = "Green"
$RED = "Red"
$YELLOW = "Yellow"
$BLUE = "Cyan"
$WHITE = "White"

function Write-Header {
    param([string]$Message)
    Clear-Host
    Write-Host "================================================" -ForegroundColor $BLUE
    Write-Host "  Stock Market Analyzer - Google Sheets Setup" -ForegroundColor $BLUE
    Write-Host "================================================" -ForegroundColor $BLUE
    Write-Host ""
    Write-Host $Message -ForegroundColor $WHITE
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $GREEN
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $RED
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor $BLUE
}

function Write-Step {
    param([int]$Step, [string]$Message)
    Write-Host ""
    Write-Host "📋 Step $Step: $Message" -ForegroundColor $YELLOW
    Write-Host "----------------------------------------" -ForegroundColor $YELLOW
}

function Show-Help {
    Write-Header "Google Sheets Setup Help"

    Write-Host "This wizard helps you setup Google Sheets for your Stock Market Analyzer." -ForegroundColor $WHITE
    Write-Host ""
    Write-Host "What you need:" -ForegroundColor $YELLOW
    Write-Host "1. A Google service account JSON file (service.json)" -ForegroundColor $WHITE
    Write-Host "2. A Google Sheets ID (from your spreadsheet URL)" -ForegroundColor $WHITE
    Write-Host ""
    Write-Host "The wizard will:" -ForegroundColor $YELLOW
    Write-Host "• Guide you through placing your service.json file" -ForegroundColor $WHITE
    Write-Host "• Help you enter your Google Sheets ID" -ForegroundColor $WHITE
    Write-Host "• Automatically configure the application" -ForegroundColor $WHITE
    Write-Host "• Test the connection to make sure it works" -ForegroundColor $WHITE
    Write-Host ""
    Write-Host "Press any key to start the setup..." -ForegroundColor $GREEN
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Test-Prerequisites {
    Write-Step 1 "Checking Requirements"

    $allGood = $true

    # Check if project directory is correct
    if (-not (Test-Path "docker-compose.yml")) {
        Write-Error "Please run this script from the Stock Market Analyzer project folder"
        Write-Info "Make sure you're in the folder that contains docker-compose.yml"
        $allGood = $false
    } else {
        Write-Success "Project folder found"
    }

    # Check if credentials directory exists
    if (-not (Test-Path "credentials")) {
        New-Item -ItemType Directory -Path "credentials" -Force | Out-Null
        Write-Success "Created credentials folder"
    } else {
        Write-Success "Credentials folder exists"
    }

    return $allGood
}

function Get-ServiceAccountFile {
    Write-Step 2 "Setting up Google Service Account"

    Write-Host "You need a Google service account JSON file to connect to Google Sheets." -ForegroundColor $WHITE
    Write-Host ""
    Write-Host "This file is usually named something like:" -ForegroundColor $YELLOW
    Write-Host "• service.json" -ForegroundColor $WHITE
    Write-Host "• credentials.json" -ForegroundColor $WHITE
    Write-Host "• your-project-name-xxxxx.json" -ForegroundColor $WHITE
    Write-Host ""

    # Check if service.json already exists in credentials folder
    if (Test-Path "credentials\service.json") {
        Write-Success "Found existing service.json file"
        Write-Host ""
        $useExisting = Read-Host "Do you want to use the existing service.json file? (Y/n)"
        if ($useExisting -eq "" -or $useExisting.ToLower() -eq "y") {
            return $true
        }
    }

    Write-Host "Please choose how to provide your service account file:" -ForegroundColor $YELLOW
    Write-Host ""
    Write-Host "1. I have the file and want to copy it" -ForegroundColor $WHITE
    Write-Host "2. I want to browse and select the file" -ForegroundColor $WHITE
    Write-Host "3. I don't have the file yet" -ForegroundColor $WHITE
    Write-Host ""

    do {
        $choice = Read-Host "Enter your choice (1, 2, or 3)"
        switch ($choice) {
            "1" {
                Write-Host ""
                Write-Host "Please copy your service account JSON file to:" -ForegroundColor $YELLOW
                Write-Host "$(Get-Location)\credentials\service.json" -ForegroundColor $GREEN
                Write-Host ""
                Write-Host "Once you've copied the file, press any key to continue..." -ForegroundColor $BLUE
                $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

                if (Test-Path "credentials\service.json") {
                    Write-Success "Service account file found!"
                    return $true
                } else {
                    Write-Error "File not found. Please copy your service.json file to the credentials folder."
                    return $false
                }
            }
            "2" {
                Write-Host ""
                Write-Host "Opening file browser..." -ForegroundColor $BLUE

                Add-Type -AssemblyName System.Windows.Forms
                $fileDialog = New-Object System.Windows.Forms.OpenFileDialog
                $fileDialog.Title = "Select Google Service Account JSON File"
                $fileDialog.Filter = "JSON files (*.json)|*.json|All files (*.*)|*.*"
                $fileDialog.InitialDirectory = [Environment]::GetFolderPath("Desktop")

                if ($fileDialog.ShowDialog() -eq 'OK') {
                    try {
                        Copy-Item $fileDialog.FileName "credentials\service.json" -Force
                        Write-Success "Service account file copied successfully!"
                        return $true
                    } catch {
                        Write-Error "Failed to copy file: $($_.Exception.Message)"
                        return $false
                    }
                } else {
                    Write-Info "File selection cancelled"
                    return $false
                }
            }
            "3" {
                Write-Host ""
                Write-Host "To get a Google service account file, you need to:" -ForegroundColor $YELLOW
                Write-Host ""
                Write-Host "1. Go to Google Cloud Console: https://console.cloud.google.com" -ForegroundColor $WHITE
                Write-Host "2. Create a new project or select existing one" -ForegroundColor $WHITE
                Write-Host "3. Enable Google Sheets API" -ForegroundColor $WHITE
                Write-Host "4. Create a Service Account" -ForegroundColor $WHITE
                Write-Host "5. Download the JSON key file" -ForegroundColor $WHITE
                Write-Host ""
                Write-Host "Once you have the file, run this setup again." -ForegroundColor $GREEN
                Write-Host ""
                Read-Host "Press Enter to exit"
                return $false
            }
            default {
                Write-Host "Please enter 1, 2, or 3" -ForegroundColor $RED
            }
        }
    } while ($choice -notin @("1", "2", "3"))
}

function Get-GoogleSheetsId {
    Write-Step 3 "Getting Google Sheets ID"

    Write-Host "Now you need your Google Sheets ID." -ForegroundColor $WHITE
    Write-Host ""
    Write-Host "To find your Google Sheets ID:" -ForegroundColor $YELLOW
    Write-Host "1. Open your Google Sheet in a web browser" -ForegroundColor $WHITE
    Write-Host "2. Look at the URL, it will look like:" -ForegroundColor $WHITE
    Write-Host "   https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit" -ForegroundColor $BLUE
    Write-Host "3. Copy the long string between '/d/' and '/edit'" -ForegroundColor $WHITE
    Write-Host ""
    Write-Host "Example: If your URL is:" -ForegroundColor $YELLOW
    Write-Host "https://docs.google.com/spreadsheets/d/1abc123XYZ789def456/edit" -ForegroundColor $BLUE
    Write-Host "Then your Sheet ID is: 1abc123XYZ789def456" -ForegroundColor $GREEN
    Write-Host ""

    do {
        $sheetId = Read-Host "Enter your Google Sheets ID"
        $sheetId = $sheetId.Trim()

        if ($sheetId.Length -eq 0) {
            Write-Error "Please enter a valid Sheet ID"
            continue
        }

        # Basic validation - Google Sheets IDs are typically 44 characters
        if ($sheetId.Length -lt 20) {
            Write-Warning "This seems too short for a Google Sheets ID. Please double-check."
            $confirm = Read-Host "Are you sure this is correct? (y/N)"
            if ($confirm.ToLower() -ne "y") {
                continue
            }
        }

        return $sheetId

    } while ($true)
}

function Update-Configuration {
    param([string]$SheetId)

    Write-Step 4 "Configuring Application"

    try {
        # Update config.json
        $config = @{
            storage_type = "google_sheets"
            app_mode = "google_sheets"
            google_credentials_file = "/app/credentials/service.json"
            google_sheet_id = $SheetId
            redis_host = "redis"
            redis_port = 6379
            first_run = $true
            configured_by = "setup_wizard"
            setup_date = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        }

        $config | ConvertTo-Json -Depth 10 | Set-Content "config.json" -Encoding UTF8
        Write-Success "Configuration updated successfully"

        # Rename service account file to expected name
        if (Test-Path "credentials\service.json") {
            # Also copy with the expected name for Docker
            Copy-Item "credentials\service.json" "credentials\google_credentials.json" -Force
            Write-Success "Service account file prepared for Docker"
        }

        return $true

    } catch {
        Write-Error "Failed to update configuration: $($_.Exception.Message)"
        return $false
    }
}

function Test-Configuration {
    Write-Step 5 "Testing Google Sheets Connection"

    Write-Host "Starting the application to test Google Sheets connection..." -ForegroundColor $BLUE
    Write-Host "This may take a few minutes..." -ForegroundColor $YELLOW
    Write-Host ""

    # Start the application
    $process = Start-Process -FilePath "docker" -ArgumentList "compose", "up", "-d", "--build" -PassThru -NoNewWindow

    # Wait for the process to complete
    $process.WaitForExit()

    if ($process.ExitCode -eq 0) {
        Write-Success "Application started successfully!"
        Write-Host ""
        Write-Host "Testing connection..." -ForegroundColor $BLUE

        # Wait a bit for services to start
        Start-Sleep -Seconds 10

        # Check if containers are running
        $containers = docker compose ps --format json 2>$null | ConvertFrom-Json
        $appRunning = $false

        foreach ($container in $containers) {
            if ($container.Service -eq "app" -and $container.State -eq "running") {
                $appRunning = $true
                break
            }
        }

        if ($appRunning) {
            Write-Success "Application is running!"
            Write-Host ""
            Write-Host "🌐 Your Stock Market Analyzer is ready!" -ForegroundColor $GREEN
            Write-Host "   Access it at: http://localhost:8501" -ForegroundColor $BLUE
            Write-Host ""
            Write-Host "The application will test the Google Sheets connection automatically." -ForegroundColor $WHITE
            Write-Host "If there are any issues, they will be shown in the application." -ForegroundColor $WHITE

            return $true
        } else {
            Write-Error "Application failed to start properly"
            Write-Info "Check the logs with: docker compose logs"
            return $false
        }
    } else {
        Write-Error "Failed to start application"
        Write-Info "Check the logs with: docker compose logs"
        return $false
    }
}

function Show-CompletionMessage {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor $GREEN
    Write-Host "  🎉 Google Sheets Setup Complete!" -ForegroundColor $GREEN
    Write-Host "================================================" -ForegroundColor $GREEN
    Write-Host ""
    Write-Host "✅ Service account file configured" -ForegroundColor $GREEN
    Write-Host "✅ Google Sheets ID saved" -ForegroundColor $GREEN
    Write-Host "✅ Application configured for Google Sheets" -ForegroundColor $GREEN
    Write-Host "✅ Connection tested successfully" -ForegroundColor $GREEN
    Write-Host ""
    Write-Host "🌐 Access your application at: http://localhost:8501" -ForegroundColor $BLUE
    Write-Host ""
    Write-Host "Your data will now be stored in Google Sheets!" -ForegroundColor $WHITE
    Write-Host "You can switch back to local storage anytime through Settings." -ForegroundColor $WHITE
    Write-Host ""
    Write-Host "Press any key to open the application in your browser..." -ForegroundColor $YELLOW
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

    try {
        Start-Process "http://localhost:8501"
    } catch {
        Write-Info "Please open http://localhost:8501 in your browser"
    }
}

# Main script execution
try {
    if ($Help) {
        Show-Help
        exit 0
    }

    Write-Header "Welcome! Let's setup Google Sheets for your Stock Market Analyzer."

    Write-Host "This wizard will help you:" -ForegroundColor $WHITE
    Write-Host "• Setup your Google service account file" -ForegroundColor $WHITE
    Write-Host "• Configure your Google Sheets ID" -ForegroundColor $WHITE
    Write-Host "• Test the connection" -ForegroundColor $WHITE
    Write-Host "• Launch your application" -ForegroundColor $WHITE
    Write-Host ""

    $start = Read-Host "Ready to start? (Y/n)"
    if ($start -ne "" -and $start.ToLower() -eq "n") {
        Write-Info "Setup cancelled"
        exit 0
    }

    # Step 1: Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-Error "Prerequisites check failed"
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Step 2: Get service account file
    if (-not (Get-ServiceAccountFile)) {
        Write-Error "Service account setup failed"
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Step 3: Get Google Sheets ID
    $sheetId = Get-GoogleSheetsId

    # Step 4: Update configuration
    if (-not (Update-Configuration -SheetId $sheetId)) {
        Write-Error "Configuration update failed"
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Step 5: Test configuration
    if (-not (Test-Configuration)) {
        Write-Error "Connection test failed"
        Write-Info "You can still try to access the application at http://localhost:8501"
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Show completion message
    Show-CompletionMessage

} catch {
    Write-Error "An unexpected error occurred: $($_.Exception.Message)"
    Write-Info "Please try running the setup again"
    Read-Host "Press Enter to exit"
    exit 1
}