# Docker Setup for Stock Market Analyzer

This guide explains how to run the Stock Market Analyzer using Docker with persistent data storage.

## Quick Start

1. **Build and run the application:**
   ```bash
   docker compose up --build
   ```

2. **Access the application:**
   - Open your browser and go to: http://localhost:8501

3. **Stop the application:**
   ```bash
   docker compose down
   ```

## Data Persistence

The Docker setup ensures all your data persists between container restarts:

- **Application Data**: Stored in Docker volume `app_data`
  - Portfolio information
  - Transaction history
  - Selected stocks
  - Configuration files

- **Redis Cache**: Stored in Docker volume `redis_data`
  - Stock price cache
  - API response cache
  - Session data

## Configuration

### Default Configuration
The application runs in Redis mode by default with the following settings:
- Redis host: `redis` (internal Docker network)
- Redis port: `6379`
- Application mode: `redis`
- Update interval: 5 minutes

### Google Sheets Integration (Optional)
To use Google Sheets storage instead of Redis:

1. Create a `credentials` directory in the project root
2. Place your Google service account credentials file as `credentials/google_credentials.json`
3. Update the `GOOGLE_SHEET_ID` environment variable in `docker-compose.yml`
4. Change `APP_MODE` to `google_sheets` in the docker-compose.yml

### Environment Variables
You can modify these in the `docker-compose.yml` file:

- `APP_MODE`: `redis` or `google_sheets`
- `YAHOO_FINANCE_ENABLED`: `true` or `false`
- `UPDATE_INTERVAL_MINUTES`: Number of minutes between updates
- `REDIS_HOST`: Redis server hostname
- `REDIS_PORT`: Redis server port

## Docker Commands

### Build and Start
```bash
# Build and start all services
docker compose up --build

# Start in detached mode (background)
docker compose up -d --build
```

### Management Commands
```bash
# Stop all services
docker compose down

# Stop and remove volumes (WARNING: This will delete all data)
docker compose down -v

# View logs
docker compose logs

# View logs for specific service
docker compose logs app
docker compose logs redis

# Follow logs in real-time
docker compose logs -f
```

### Data Management
```bash
# Backup application data
docker run --rm -v stock_market_analyzer_app_data:/data -v $(pwd):/backup alpine tar czf /backup/app_data_backup.tar.gz -C /data .

# Restore application data
docker run --rm -v stock_market_analyzer_app_data:/data -v $(pwd):/backup alpine tar xzf /backup/app_data_backup.tar.gz -C /data

# View volume information
docker volume ls
docker volume inspect stock_market_analyzer_app_data
docker volume inspect stock_market_analyzer_redis_data
```

## Troubleshooting

### Application Won't Start
1. Check if ports 8501 and 6379 are already in use:
   ```bash
   netstat -an | grep :8501
   netstat -an | grep :6379
   ```

2. View container logs:
   ```bash
   docker compose logs app
   ```

### Data Not Persisting
1. Verify volumes are created:
   ```bash
   docker volume ls
   ```

2. Check volume mounts:
   ```bash
   docker compose config
   ```

### Redis Connection Issues
1. Check Redis container status:
   ```bash
   docker compose ps redis
   ```

2. Test Redis connectivity:
   ```bash
   docker compose exec redis redis-cli ping
   ```

### Network Issues
1. Check Docker network:
   ```bash
   docker network ls
   docker network inspect stock_analyzer_network
   ```

## Health Checks

Both services include health checks:
- **Redis**: Responds to `PING` command
- **App**: HTTP health endpoint at `/_stcore/health`

Check health status:
```bash
docker compose ps
```

## Performance Tuning

### Redis Memory Management
Redis is configured with:
- Maximum memory: 256MB
- Eviction policy: `allkeys-lru` (removes least recently used keys)
- Persistence: AOF (Append Only File) enabled

### Application Resources
You can limit resources by adding to the `docker-compose.yml`:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
```

## Security Notes

- Redis is not exposed to the host network by default
- Google credentials are mounted read-only
- Health checks help ensure service availability
- No sensitive data is logged in container output

## Development Mode

For development, you can mount the source code:

```yaml
services:
  app:
    volumes:
      - .:/app
      - app_data:/app/data
```

This allows you to edit code without rebuilding the container.