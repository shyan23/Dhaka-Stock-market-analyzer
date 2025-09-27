# 🚀 Stock Market Analyzer - Windows Setup Guide

**A complete guide for non-technical users to setup and run the Stock Market Analyzer on Windows**

---

## 📋 What You'll Get

After following this guide, you'll have:
- ✅ A fully functional Stock Market Analyzer running on your Windows computer
- ✅ Real-time Dhaka Stock Exchange (DSE) data tracking
- ✅ Portfolio management with profit/loss tracking
- ✅ Transaction recording and history
- ✅ Professional charts and reports
- ✅ Choice between local database or Google Sheets storage
- ✅ Data that persists even when you restart your computer

---

## 🖥️ System Requirements

- **Windows 10** or **Windows 11**
- **4GB RAM** minimum (8GB recommended)
- **2GB free disk space**
- **Internet connection** for stock data
- **Administrator access** for installation

---

## 📥 Step 1: Download Required Software

### 1.1 Download Docker Desktop

1. Go to: https://www.docker.com/products/docker-desktop
2. Click **"Download for Windows"**
3. Save the file to your Downloads folder

### 1.2 Download the Stock Market Analyzer

1. Go to the project repository (provided by your developer)
2. Click the **green "Code" button**
3. Select **"Download ZIP"**
4. Save to your Desktop and extract the folder

---

## 🛠️ Step 2: Install Docker Desktop

### 2.1 Run the Docker Installer

1. **Right-click** on the downloaded Docker installer
2. Select **"Run as administrator"**
3. Follow the installation wizard:
   - ✅ Check **"Use WSL 2 instead of Hyper-V"** (if shown)
   - ✅ Check **"Add shortcut to desktop"**
   - Click **"Ok"** and wait for installation

### 2.2 Restart Your Computer

1. Restart Windows when prompted
2. Docker Desktop should start automatically after restart
3. You'll see a Docker whale icon in your system tray

### 2.3 Complete Docker Setup

1. **Accept the Docker Desktop Service Agreement**
2. **Skip the sign-in** (click "Continue without signing in")
3. **Skip the survey** (click "Skip survey")
4. Wait for Docker Engine to start (this may take a few minutes)

✅ **You'll know Docker is ready when you see "Docker Desktop is running" in the system tray**

---

## 🚀 Step 3: Launch the Stock Market Analyzer

### 3.1 Open the Project Folder

1. Navigate to your **Desktop**
2. Open the extracted **stock_market_analyzer** folder
3. You should see files like `deploy-windows.ps1`, `docker-compose.yml`, etc.

### 3.2 Run the Deployment Script

**Method 1: Using PowerShell (Recommended)**

1. **Right-click** in the project folder
2. Select **"Open in Terminal"** or **"Open PowerShell window here"**
3. Type this command and press Enter:
   ```powershell
   .\deploy-windows.ps1 start
   ```

**Method 2: Using File Explorer**

1. **Right-click** on `deploy-windows.ps1`
2. Select **"Run with PowerShell"**
3. If prompted about execution policy, type `Y` and press Enter

### 3.3 Wait for Setup to Complete

The script will:
- ✅ Check if Docker is running
- ✅ Download required components
- ✅ Build the application
- ✅ Start all services
- ✅ Initialize the database

**This may take 5-10 minutes on first run** ⏰

---

## 🌐 Step 4: Access Your Application

### 4.1 Open the Application

1. Once setup is complete, you'll see:
   ```
   ✅ Application started successfully!
   🌐 Access your application at: http://localhost:8501
   ```

2. **Click the link** or open your web browser and go to:
   ```
   http://localhost:8501
   ```

### 4.2 First Time Setup

1. The application will guide you through initial setup
2. Choose your storage option:
   - **Redis Database** (Recommended for beginners)
   - **Google Sheets** (For cloud storage)

3. Start adding stocks to track and manage your portfolio!

---

## 🎯 Daily Usage

### Starting the Application

**Option 1: Double-click method**
1. Go to your project folder
2. Double-click `deploy-windows.ps1`
3. Wait for "Application started successfully!" message
4. Open http://localhost:8501 in your browser

**Option 2: PowerShell method**
1. Open PowerShell in project folder
2. Run: `.\deploy-windows.ps1 start`

### Stopping the Application

**Option 1: PowerShell**
```powershell
.\deploy-windows.ps1 stop
```

**Option 2: Docker Desktop**
1. Open Docker Desktop
2. Go to "Containers" tab
3. Click stop button on "stock_market_analyzer" containers

### Checking Status

```powershell
.\deploy-windows.ps1 -Status
```

### Viewing Logs (for troubleshooting)

```powershell
.\deploy-windows.ps1 -Logs
```

---

## 🔧 Useful Commands Reference

| Command | Description |
|---------|-------------|
| `.\deploy-windows.ps1 start` | Start the application |
| `.\deploy-windows.ps1 stop` | Stop the application |
| `.\deploy-windows.ps1 restart` | Restart the application |
| `.\deploy-windows.ps1 build` | Rebuild and start |
| `.\deploy-windows.ps1 -Status` | Check if running |
| `.\deploy-windows.ps1 -Logs` | View application logs |
| `.\deploy-windows.ps1 -Update` | Update to latest version |
| `.\deploy-windows.ps1 -Help` | Show all commands |

---

## 🔄 Switching Between Storage Types

You can switch between local database and Google Sheets **without losing data**:

1. Open the application: http://localhost:8501
2. Go to **Settings** in the sidebar
3. Scroll down to **"Storage Backend Switching"**
4. Select your preferred storage type
5. Click **"Migrate"**
6. Your data will be safely transferred!

### Setting Up Google Sheets (Optional)

1. Get a Google service account JSON file from your developer
2. Place it in the `credentials` folder as `google_credentials.json`
3. Create a new Google Sheet and note its ID
4. Use the migration feature to switch to Google Sheets

---

## ❓ Troubleshooting

### Problem: "Docker is not running"

**Solution:**
1. Look for Docker whale icon in system tray
2. If not there, start Docker Desktop from Start menu
3. Wait for "Docker Desktop is running" message

### Problem: "Port 8501 is already in use"

**Solution:**
1. Close any other applications using port 8501
2. Or restart your computer and try again

### Problem: Script execution policy error

**Solution:**
1. Open PowerShell as Administrator
2. Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. Type `Y` when prompted
4. Try running the script again

### Problem: Application won't load in browser

**Solution:**
1. Wait 2-3 minutes after starting (initial setup takes time)
2. Try refreshing the browser page
3. Check status with: `.\deploy-windows.ps1 -Status`
4. Check logs with: `.\deploy-windows.ps1 -Logs`

### Problem: "Failed to start application"

**Solution:**
1. Make sure Docker Desktop is running
2. Check for Windows updates
3. Restart Docker Desktop
4. Try: `.\deploy-windows.ps1 build`

---

## 🔐 Data Safety & Backup

### Your Data is Safe

- ✅ All data is stored in persistent Docker volumes
- ✅ Data survives computer restarts
- ✅ Data survives application updates
- ✅ You can backup and restore anytime

### Creating Backups

1. Open the application: http://localhost:8501
2. Go to **Settings** → **Data Management**
3. Click **"Create Backup"**
4. Download the backup file to a safe location

### Restoring from Backup

1. Go to **Settings** → **Data Management**
2. Upload your backup file
3. Click **"Restore from Backup"**

---

## 🆘 Getting Help

### If You Need Assistance

1. **Check the logs first**: `.\deploy-windows.ps1 -Logs`
2. **Try restarting**: `.\deploy-windows.ps1 restart`
3. **Contact your developer** with:
   - Screenshots of any error messages
   - Copy of the log output
   - Description of what you were trying to do

### Self-Help Resources

- **Application Help**: Look for the ❓ help icons in the application
- **Command Help**: Run `.\deploy-windows.ps1 -Help`
- **Docker Help**: Check Docker Desktop settings and documentation

---

## 🎉 You're All Set!

Congratulations! You now have a fully functional Stock Market Analyzer running on your Windows computer.

**Key Features to Explore:**

- 📊 **Dashboard**: Overview of your tracked stocks
- 🔍 **Stock Selector**: Search and add stocks to track
- 💼 **Portfolio**: Manage your investments
- 💰 **Transactions**: Record buy/sell transactions
- 📈 **Price Tracker**: Monitor stock performance
- ⚙️ **Settings**: Configure and manage your data

**Enjoy tracking your investments!** 🚀

---

*This guide was created to make stock market analysis accessible to everyone. Happy investing! 💹*