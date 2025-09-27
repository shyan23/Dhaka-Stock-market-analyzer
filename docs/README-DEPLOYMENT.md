# 🐳 Stock Market Analyzer - Docker Deployment

## 🌟 Features

✅ **Complete Dockerization** - Run with `docker compose up --build`
✅ **Persistent Data** - All data survives container restarts
✅ **Storage Switching** - Seamlessly switch between Redis ↔ Google Sheets
✅ **Windows Ready** - PowerShell and batch scripts for easy deployment
✅ **Zero Data Loss** - Built-in migration and backup system

---

## 🚀 Quick Start

### For Non-Technical Users (Windows)
1. **Download** Docker Desktop: https://www.docker.com/products/docker-desktop
2. **Extract** this project to your Desktop
3. **Double-click** `deploy-windows.bat`
4. **Open** http://localhost:8501

### For Developers (Any Platform)
```bash
# Clone and start
git clone <repository>
cd stock_market_analyzer
docker compose up --build

# Access at http://localhost:8501
```

---

## 📂 Project Structure

```
stock_market_analyzer/
├── 🚀 deploy-windows.ps1      # PowerShell deployment script
├── 🚀 deploy-windows.bat      # Batch file alternative
├── 🐳 docker-compose.yml      # Docker orchestration
├── 🐳 Dockerfile             # Application container
├── ⚙️ config.json            # Runtime configuration
├── 📁 credentials/           # Google Sheets credentials (optional)
├── 📚 WINDOWS-SETUP-GUIDE.md # Complete setup guide
├── 📚 QUICK-START.md         # 5-minute start guide
└── 🔧 src/                   # Application source code
```

---

## 🔄 Storage Backend Switching

**The app supports seamless switching between storage types:**

### 🗄️ Redis Database (Default)
- **Local storage** within Docker container
- **Fast performance** with caching
- **No external dependencies**
- **Data persists** in Docker volumes

### 📈 Google Sheets
- **Cloud storage** synced to Google Sheets
- **Real-time collaboration** possible
- **External backup** automatically
- **Requires** Google service account

### Migration Process
1. Go to **Settings** → **Storage Backend Switching**
2. Select target storage type
3. Configure credentials (if Google Sheets)
4. Click **Migrate** - system handles everything!
5. **Zero data loss** - full backup and restore

---

## 🖥️ Windows Deployment Options

### Option 1: PowerShell Script (Recommended)
```powershell
# Start application
.\deploy-windows.ps1 start

# Other commands
.\deploy-windows.ps1 stop
.\deploy-windows.ps1 restart
.\deploy-windows.ps1 -Status
.\deploy-windows.ps1 -Logs
.\deploy-windows.ps1 -Help
```

### Option 2: Batch File (Simplest)
```cmd
# Just double-click
deploy-windows.bat
```

### Option 3: Manual Docker Commands
```cmd
docker compose up -d --build
```

---

## 💾 Data Persistence Architecture

### Volume Mapping
- **app_data** → `/app/data` → Application data (portfolio, transactions)
- **redis_data** → `/data` → Redis database and cache
- **credentials** → `/app/credentials` → Google Sheets credentials
- **config.json** → `/app/config.json` → Runtime configuration

### Data Survival
✅ **Container restarts** - Data remains in volumes
✅ **System reboots** - Volumes persist on disk
✅ **Application updates** - Data preserved during rebuilds
✅ **Storage switching** - Automatic backup and restore

---

## 🌐 Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Main App** | http://localhost:8501 | Streamlit web interface |
| **Redis** | localhost:6379 | Database (internal use) |

---

## 🛠️ Advanced Configuration

### Environment Variables
```yaml
# Storage Configuration
APP_MODE: redis                    # 'redis' or 'google_sheets'
REDIS_HOST: redis                  # Redis hostname
REDIS_PORT: 6379                   # Redis port

# Google Sheets (Optional)
GOOGLE_CREDENTIALS_FILE: /app/credentials/google_credentials.json
GOOGLE_SHEET_ID: your_sheet_id

# Application Settings
UPDATE_INTERVAL_MINUTES: 5         # Data refresh interval
YAHOO_FINANCE_ENABLED: true       # Enable YFinance fallback
```

### Google Sheets Setup
1. Create Google Cloud service account
2. Download JSON credentials file
3. Place in `credentials/google_credentials.json`
4. Create target Google Sheet
5. Share sheet with service account email
6. Use migration feature to switch storage

---

## 🔧 Troubleshooting

### Common Issues

**Docker not running**
```powershell
# Check Docker status
.\deploy-windows.ps1 -Status

# Start Docker Desktop manually
```

**Port conflicts**
```bash
# Check what's using port 8501
netstat -an | findstr :8501

# Kill conflicting processes or change port
```

**Storage migration failed**
- Check Google Sheets credentials
- Ensure target sheet exists and is accessible
- Verify Redis connection
- Check logs: `.\deploy-windows.ps1 -Logs`

**Data not persisting**
- Verify volumes exist: `docker volume ls`
- Check volume mounts: `docker compose config`
- Ensure proper shutdown: `docker compose down`

### Logs and Debugging
```powershell
# View all logs
.\deploy-windows.ps1 -Logs

# Check container status
.\deploy-windows.ps1 -Status

# Rebuild from scratch
.\deploy-windows.ps1 -Cleanup
.\deploy-windows.ps1 build
```

---

## 🔐 Security & Backup

### Data Security
- Redis password protected (configurable)
- Google credentials mounted read-only
- No sensitive data in logs
- Local data encrypted at rest (Docker volume)

### Backup Strategy
1. **Automatic backups** during storage migration
2. **Manual backups** via Settings → Data Management
3. **Volume backups** using Docker commands:
   ```bash
   # Backup volumes
   docker run --rm -v stock_market_analyzer_app_data:/data -v $(pwd):/backup alpine tar czf /backup/app_backup.tar.gz -C /data .

   # Restore volumes
   docker run --rm -v stock_market_analyzer_app_data:/data -v $(pwd):/backup alpine tar xzf /backup/app_backup.tar.gz -C /data
   ```

---

## 🎯 Production Deployment

### Docker Compose Override
Create `docker-compose.override.yml` for production:
```yaml
services:
  app:
    environment:
      - UPDATE_INTERVAL_MINUTES=1
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  redis:
    environment:
      - REDIS_PASSWORD=your_secure_password
```

### Scaling Considerations
- Redis memory limits configured (256MB default)
- Health checks enabled for both services
- Restart policies set to `unless-stopped`
- Network isolation with custom network

---

## 📋 Maintenance

### Regular Tasks
```powershell
# Update application
.\deploy-windows.ps1 -Update

# View resource usage
docker stats

# Clean unused resources
docker system prune

# Backup data
# Use Settings → Data Management → Create Backup
```

### Health Monitoring
- Built-in health checks for all services
- Service status via: `.\deploy-windows.ps1 -Status`
- Logs monitoring via: `.\deploy-windows.ps1 -Logs`

---

## 🎉 Success!

Your Stock Market Analyzer is now fully dockerized with:

✅ **One-command deployment**
✅ **Persistent data storage**
✅ **Seamless storage switching**
✅ **Windows-friendly scripts**
✅ **Professional architecture**

**Access your app**: http://localhost:8501
**Manage with**: `.\deploy-windows.ps1 -Help`

Happy stock tracking! 📈🚀