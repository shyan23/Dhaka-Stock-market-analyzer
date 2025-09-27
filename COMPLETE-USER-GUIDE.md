# 📈 Stock Market Analyzer - Complete User Guide

**Your comprehensive guide from download to daily usage**

---

## 📖 Table of Contents

1. [Overview](#-overview)
2. [System Requirements](#-system-requirements)
3. [Initial Setup](#-initial-setup)
4. [Storage Options](#-storage-options)
5. [Running the Application](#-running-the-application)
6. [Using the Application](#-using-the-application)
7. [Daily Operations](#-daily-operations)
8. [Advanced Features](#-advanced-features)
9. [Troubleshooting](#-troubleshooting)
10. [Maintenance & Backup](#-maintenance--backup)

---

## 🎯 Overview

The Stock Market Analyzer is a comprehensive web application designed specifically for tracking the Dhaka Stock Exchange (DSE). It provides real-time stock data, portfolio management, transaction recording, and professional reporting capabilities.

### Key Features
- ✅ **Real-time DSE data** with market status tracking
- ✅ **Portfolio management** with profit/loss analysis
- ✅ **Transaction recording** with detailed history
- ✅ **Interactive charts** and technical analysis
- ✅ **Dual storage backends** (Local Redis + Google Sheets)
- ✅ **Professional reports** (PDF, Excel, CSV exports)
- ✅ **Data persistence** across restarts
- ✅ **Seamless storage migration** with zero data loss

---

## 💻 System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 or Windows 11
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free disk space
- **Internet**: Stable connection for stock data
- **Access**: Administrator privileges for installation

### Required Software
- **Docker Desktop** (will be installed in setup)
- **Web Browser** (Chrome, Firefox, Edge, or Safari)

---

## 🚀 Initial Setup

### Step 1: Download Docker Desktop

1. **Visit**: https://www.docker.com/products/docker-desktop
2. **Click**: "Download for Windows"
3. **Save** the installer to your Downloads folder

### Step 2: Install Docker Desktop

1. **Right-click** the Docker installer → **"Run as administrator"**
2. **Follow the installation wizard:**
   - ✅ Check "Use WSL 2 instead of Hyper-V" (if shown)
   - ✅ Check "Add shortcut to desktop"
   - Click "Ok" and wait for installation
3. **Restart your computer** when prompted
4. **Start Docker Desktop** (should start automatically)
5. **Complete Docker setup:**
   - Accept the Service Agreement
   - Skip sign-in (click "Continue without signing in")
   - Skip the survey
   - Wait for "Docker Desktop is running" message

### Step 3: Download the Stock Market Analyzer

1. **Go to the GitHub repository** (provided by your developer)
2. **Click** the green "Code" button
3. **Select** "Download ZIP"
4. **Save to Desktop** and extract the folder
5. **Rename** the folder to `stock_market_analyzer` (if needed)

### Step 4: Verify Installation

1. **Open** the `stock_market_analyzer` folder
2. **Look for these key files:**
   - `deploy-windows.bat`
   - `deploy-windows.ps1`
   - `docker-compose.yml`
   - `setup-google-sheets.bat`

✅ **You're ready to proceed!**

---

## 💾 Storage Options

The application supports two storage backends that you can switch between seamlessly:

### Option 1: Redis Database (Recommended for Beginners)

**Pros:**
- ✅ **No setup required** - works immediately
- ✅ **Fast performance** with local caching
- ✅ **No external dependencies**
- ✅ **Private and secure** (data stays on your computer)

**Cons:**
- ❌ **Local only** - data doesn't sync to cloud
- ❌ **Single computer** access

### Option 2: Google Sheets (Advanced Users)

**Pros:**
- ✅ **Cloud storage** - access from anywhere
- ✅ **Real-time collaboration** possible
- ✅ **Automatic backup** to Google Drive
- ✅ **Data sharing** capabilities

**Cons:**
- ❌ **Requires setup** (Google service account)
- ❌ **Internet dependent**
- ❌ **Google account required**

### Choosing Your Storage

**Start with Redis Database** if you:
- Want to get started immediately
- Prefer keeping data local
- Don't need cloud access

**Use Google Sheets** if you:
- Want cloud backup
- Need to access from multiple devices
- Want to share data with others
- Have a Google service account

**Note**: You can switch between storage types anytime without losing data!

---

## 🏃‍♂️ Running the Application

### Method 1: Quick Start (Redis Database)

**For immediate use without Google Sheets:**

1. **Open** the `stock_market_analyzer` folder
2. **Double-click** `deploy-windows.bat`
3. **Wait** for the setup to complete (5-10 minutes first time)
4. **Application opens** automatically in your browser
5. **Start using** the app at http://localhost:8501

### Method 2: Google Sheets Setup

**If you want to use Google Sheets storage:**

1. **Get your Google credentials:**
   - Obtain `service.json` file from your developer
   - Find your Google Sheets ID (see guide below)

2. **Run the Google Sheets setup:**
   - **Double-click** `setup-google-sheets.bat`
   - **Follow the wizard** prompts
   - **Provide** service.json file and Sheets ID
   - **Wait** for automatic configuration and testing

3. **Start the application:**
   - **Double-click** `deploy-windows.bat`
   - **Access** at http://localhost:8501

### Method 3: PowerShell (Advanced Users)

**For more control and troubleshooting:**

```powershell
# Navigate to project folder in PowerShell
cd "path\to\stock_market_analyzer"

# Start application
.\deploy-windows.ps1 start

# Other useful commands
.\deploy-windows.ps1 -Status    # Check status
.\deploy-windows.ps1 -Logs      # View logs
.\deploy-windows.ps1 stop       # Stop application
.\deploy-windows.ps1 restart    # Restart application
.\deploy-windows.ps1 -Help      # Show all commands
```

---

## 📊 Using the Application

### First Time Access

1. **Open your browser** to http://localhost:8501
2. **Wait** for the application to load (may take 30 seconds)
3. **You'll see** the Stock Market Analyzer dashboard

### Main Interface Overview

The application has **5 main sections** accessible from the sidebar:

#### 1. 📊 Dashboard
- **Market overview** with current status
- **Quick stats** of your tracked stocks
- **Portfolio summary** with total value
- **Recent price movements**

#### 2. 🔍 Stock Selector
- **Search stocks** by symbol or name
- **Add stocks** to your tracking list
- **Popular DSE stocks** quick-add buttons
- **Stock details** and current prices

#### 3. 💼 Portfolio
- **Current holdings** with quantities
- **Profit/Loss analysis** with percentages
- **Average cost** vs current price
- **Portfolio performance** charts

#### 4. 💰 Transactions
- **Record buy/sell** transactions
- **Transaction history** with filtering
- **Automatic portfolio** updates
- **Smart price features** (last price, current price)

#### 5. 📈 Price Tracker
- **Real-time price monitoring**
- **Interactive charts** (candlestick, line, volume)
- **Historical data** analysis
- **Price alerts** and notifications

#### 6. ⚙️ Settings
- **Storage backend switching**
- **API configuration**
- **Export and reports**
- **Data management**

---

## 🎯 Daily Operations

### Adding Stocks to Track

1. **Go to** Stock Selector page
2. **Search** for stocks by typing symbol or name
3. **Click "Add"** next to stocks you want to track
4. **Or use** popular stocks quick-add buttons

### Recording Transactions

1. **Go to** Transactions page
2. **Click** "Add New Transaction"
3. **Fill in details:**
   - Stock symbol (dropdown of tracked stocks)
   - Transaction type (Buy/Sell)
   - Quantity
   - Price per share
   - Date (defaults to today)
   - Notes (optional)
4. **Click** "Save Transaction"
5. **Portfolio updates** automatically

### Monitoring Your Portfolio

1. **Go to** Portfolio page
2. **View current holdings** with:
   - Current value vs cost
   - Profit/Loss amounts and percentages
   - Total portfolio performance
3. **Click on stocks** for detailed analysis

### Viewing Stock Charts

1. **Go to** Price Tracker page
2. **Select stock** from dropdown
3. **Choose chart type:**
   - Candlestick (OHLC data)
   - Line chart (closing prices)
   - Volume chart
4. **Adjust time period** (1D, 1W, 1M, 3M, 1Y)

### Generating Reports

1. **Go to** Settings → Export & Reports
2. **Choose report type:**
   - **PDF Report**: Comprehensive portfolio analysis
   - **Portfolio CSV**: Holdings data for Excel
   - **Transactions CSV**: Complete transaction history
   - **Stock Data CSV**: Current prices of tracked stocks
   - **Excel Report**: Multi-sheet comprehensive export

---

## 🔄 Advanced Features

### Switching Storage Backends

**You can seamlessly switch between Redis and Google Sheets:**

1. **Go to** Settings → Storage Backend Switching
2. **View current** storage type and statistics
3. **Select target** storage type
4. **Configure** credentials (if switching to Google Sheets)
5. **Test connection** to ensure target is accessible
6. **Click "Migrate"** - system handles everything automatically
7. **All data transfers** safely with zero loss

### Google Sheets Integration

**Setting up Google Sheets storage:**

1. **Obtain Google service account:**
   - Create Google Cloud project
   - Enable Google Sheets API
   - Create service account
   - Download JSON credentials file

2. **Create target Google Sheet:**
   - Create new Google Sheets document
   - Share with service account email
   - Note the Sheet ID from URL

3. **Run setup wizard:**
   - Double-click `setup-google-sheets.bat`
   - Provide credentials file and Sheet ID
   - Wizard tests connection and configures everything

### Finding Google Sheets ID

**To get your Google Sheets ID:**

1. **Open your Google Sheet** in browser
2. **Look at the URL** in address bar:
   ```
   https://docs.google.com/spreadsheets/d/1abc123XYZ789def456/edit
   ```
3. **Copy the ID** between `/d/` and `/edit`:
   ```
   1abc123XYZ789def456
   ```

### Data Export Options

**Multiple export formats available:**

- **PDF Reports**: Professional portfolio analysis with charts
- **CSV Files**: For Excel analysis and external tools
- **Excel Workbooks**: Multi-sheet comprehensive data
- **JSON Backups**: Complete application state for restoration

### API Configuration

**Customize data sources:**

- **Update intervals**: How often to refresh stock data
- **API endpoints**: DSE data source URLs
- **Fallback options**: Yahoo Finance backup data
- **Connection testing**: Verify API accessibility

---

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### Application Won't Start

**Problem**: Double-clicking deploy-windows.bat shows errors

**Solutions**:
1. **Check Docker Desktop**: Look for whale icon in system tray
2. **Start Docker Desktop**: Open from Start menu if not running
3. **Wait for Docker**: Allow 2-3 minutes for Docker to fully start
4. **Try again**: Re-run deploy-windows.bat
5. **Check logs**: Run `.\deploy-windows.ps1 -Logs` in PowerShell

#### Browser Won't Load Application

**Problem**: http://localhost:8501 doesn't work

**Solutions**:
1. **Wait longer**: Initial startup takes 2-5 minutes
2. **Check port**: Ensure nothing else uses port 8501
3. **Refresh browser**: Press F5 or refresh button
4. **Try different browser**: Chrome, Firefox, or Edge
5. **Check firewall**: Allow Docker through Windows Firewall

#### Google Sheets Connection Failed

**Problem**: Migration to Google Sheets fails

**Solutions**:
1. **Verify credentials**: Ensure service.json file is correct
2. **Check Sheet ID**: Verify ID is copied correctly from URL
3. **Check permissions**: Sheet must be shared with service account
4. **Test manually**: Use setup wizard to test connection
5. **Check internet**: Ensure stable internet connection

#### Data Not Persisting

**Problem**: Data disappears after restart

**Solutions**:
1. **Check volumes**: Run `docker volume ls` to verify volumes exist
2. **Proper shutdown**: Use `.\deploy-windows.ps1 stop` instead of force-closing
3. **Storage type**: Verify your storage configuration in Settings
4. **Backup data**: Create backup before troubleshooting

#### Performance Issues

**Problem**: Application runs slowly

**Solutions**:
1. **Restart Docker**: Stop and start Docker Desktop
2. **Clear cache**: In app Settings, clear cached data
3. **Reduce stocks**: Track fewer stocks if using many
4. **Check memory**: Ensure sufficient RAM available
5. **Update Docker**: Install latest Docker Desktop version

#### PowerShell Execution Policy

**Problem**: "Execution policy" error when running scripts

**Solutions**:
1. **Open PowerShell as Administrator**
2. **Run command**: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. **Type Y** when prompted
4. **Try script again**

### Getting Help

**If issues persist:**

1. **Check logs**:
   ```powershell
   .\deploy-windows.ps1 -Logs
   ```

2. **Check status**:
   ```powershell
   .\deploy-windows.ps1 -Status
   ```

3. **Restart everything**:
   ```powershell
   .\deploy-windows.ps1 restart
   ```

4. **Contact developer** with:
   - Screenshots of error messages
   - Copy of log output
   - Description of what you were trying to do
   - Your Windows version and Docker version

---

## 🔧 Maintenance & Backup

### Regular Maintenance

#### Weekly Tasks
- **Create backup** via Settings → Data Management
- **Check Docker updates** in Docker Desktop
- **Verify data integrity** using built-in checks

#### Monthly Tasks
- **Update application** using `.\deploy-windows.ps1 -Update`
- **Clean unused resources** with `docker system prune`
- **Review and export** reports for tax purposes

### Backup Strategies

#### 1. Application Backup
**Via Settings UI:**
1. **Go to** Settings → Data Management
2. **Click** "Create Backup"
3. **Download** backup file to safe location
4. **Store** on external drive or cloud storage

#### 2. Docker Volume Backup
**Via PowerShell:**
```powershell
# Backup application data
docker run --rm -v stock_market_analyzer_app_data:/data -v ${PWD}:/backup alpine tar czf /backup/app_backup.tar.gz -C /data .

# Backup Redis data
docker run --rm -v stock_market_analyzer_redis_data:/data -v ${PWD}:/backup alpine tar czf /backup/redis_backup.tar.gz -C /data .
```

#### 3. Google Sheets Backup
**Automatic** if using Google Sheets storage:
- Data automatically synced to Google Drive
- Access Google Sheets directly for manual export
- Download as Excel or CSV from Google Sheets interface

### Data Restoration

#### From Application Backup
1. **Go to** Settings → Data Management
2. **Upload** backup file
3. **Click** "Restore from Backup"
4. **Restart** application

#### From Docker Volume Backup
```powershell
# Restore application data
docker run --rm -v stock_market_analyzer_app_data:/data -v ${PWD}:/backup alpine tar xzf /backup/app_backup.tar.gz -C /data

# Restart application
.\deploy-windows.ps1 restart
```

### Version Updates

**To update to a new version:**

1. **Backup your data** first
2. **Download new version** from GitHub
3. **Stop current application**:
   ```powershell
   .\deploy-windows.ps1 stop
   ```
4. **Copy your data files**:
   - `config.json`
   - `credentials/` folder
   - Any backup files
5. **Extract new version** over old folder
6. **Copy back your data files**
7. **Start application**:
   ```powershell
   .\deploy-windows.ps1 start
   ```

### Storage Migration

**If you need to change storage types:**

1. **Create full backup** before migration
2. **Use Settings** → Storage Backend Switching
3. **Test target storage** before migrating
4. **Monitor migration progress**
5. **Verify data integrity** after migration

---

## 🎉 Conclusion

Congratulations! You now have a complete understanding of the Stock Market Analyzer from initial setup to advanced usage.

### Quick Reference Card

**Daily Use:**
- **Start**: Double-click `deploy-windows.bat`
- **Access**: http://localhost:8501
- **Stop**: `.\deploy-windows.ps1 stop`

**Key Features:**
- **Track stocks**: Stock Selector page
- **Record trades**: Transactions page
- **Monitor portfolio**: Portfolio page
- **View charts**: Price Tracker page
- **Generate reports**: Settings → Export

**Storage:**
- **Switch storage**: Settings → Storage Backend Switching
- **Setup Google Sheets**: Double-click `setup-google-sheets.bat`
- **Backup data**: Settings → Data Management

**Troubleshooting:**
- **Check logs**: `.\deploy-windows.ps1 -Logs`
- **Check status**: `.\deploy-windows.ps1 -Status`
- **Restart**: `.\deploy-windows.ps1 restart`

### Support

For additional support:
- **Review this guide** for comprehensive information
- **Check troubleshooting section** for common issues
- **Contact your developer** with specific problems
- **Include screenshots** and log output when reporting issues

**Happy investing with your Stock Market Analyzer!** 📈💰

---

*This guide covers everything you need to know to successfully use the Stock Market Analyzer. Keep this guide handy for reference and share it with other users.*