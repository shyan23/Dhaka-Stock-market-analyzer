# Redis Setup for Streamlit Cloud Deployment

## Why Redis is Essential

Your multi-user stock analyzer **requires** Redis for:
- ✅ **Persistent user data** (portfolios, transactions, cash balances)
- ✅ **Multi-user separation** (each user's data isolated)
- ✅ **Session persistence** (data survives browser refresh/restart)
- ✅ **Cloud deployment** (data survives app restarts)

## Quick Setup Options (Choose One)

### Option 1: Upstash Redis (Recommended - Free)

1. **Create Account**: Go to [upstash.com](https://upstash.com)
2. **Create Database**:
   - Click "Create Database"
   - Choose "Global" for better performance
   - Free tier: 10,000 commands/day
3. **Get Connection Details**:
   ```
   Endpoint: redis-xxxxx.upstash.io
   Port: 6379
   Password: your-password-here
   ```

### Option 2: Railway Redis (Easy)

1. **Create Account**: Go to [railway.app](https://railway.app)
2. **New Project**: Click "New Project" → "Add Redis"
3. **Get Connection String**: Copy the `REDIS_URL` from dashboard
   ```
   redis://:password@host:port
   ```

### Option 3: Redis Cloud (Comprehensive)

1. **Create Account**: Go to [redis.com](https://redis.com/try-free/)
2. **Create Database**: Free 30MB database
3. **Get Connection Details** from dashboard

## Streamlit Cloud Configuration

### Method 1: Using Streamlit Secrets (Recommended)

1. **Go to your Streamlit Cloud app settings**
2. **Add to secrets.toml**:
   ```toml
   [redis]
   host = "redis-xxxxx.upstash.io"
   port = 6379
   password = "your-password-here"

   # Or use connection URL
   [redis]
   url = "redis://:password@host:port"
   ```

### Method 2: Environment Variables

Add these to your Streamlit Cloud environment:
```bash
REDIS_HOST=redis-xxxxx.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=your-password-here
```

## Update Your Config

Update `config.py` to use Redis secrets:

```python
import streamlit as st

class Config:
    def __init__(self):
        # Redis Configuration
        if "redis" in st.secrets:
            self.REDIS_HOST = st.secrets["redis"]["host"]
            self.REDIS_PORT = st.secrets["redis"]["port"]
            self.REDIS_PASSWORD = st.secrets["redis"]["password"]
        else:
            # Fallback to environment variables
            self.REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
            self.REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
            self.REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
```

## Test Your Redis Connection

Create a test script to verify Redis works:

```python
import redis
import streamlit as st

def test_redis():
    try:
        if "redis" in st.secrets:
            redis_client = redis.Redis(
                host=st.secrets["redis"]["host"],
                port=st.secrets["redis"]["port"],
                password=st.secrets["redis"]["password"],
                decode_responses=True
            )
        else:
            redis_client = redis.Redis(
                host='localhost',
                port=6379,
                decode_responses=True
            )

        # Test connection
        redis_client.ping()
        redis_client.set("test_key", "Hello Redis!")
        result = redis_client.get("test_key")

        st.success(f"✅ Redis connected! Test result: {result}")
        return True

    except Exception as e:
        st.error(f"❌ Redis connection failed: {e}")
        return False
```

## Data Structure in Redis

Your app will store data like this:

```python
# User-specific keys
"user_john_doe_portfolio_items"     # John's portfolio
"user_jane_smith_transactions"      # Jane's transactions
"user_demo_user_cash_balance"       # Demo user's cash

# Global settings
"app:portfolio_settings"            # App-wide settings
"app:storage_preference"            # Storage preferences
```

## Production Recommendations

1. **Use SSL/TLS**: Most Redis providers offer secure connections
2. **Monitor Usage**: Free tiers have command limits
3. **Backup Strategy**: Export user data regularly
4. **Connection Pooling**: Redis handles this automatically

## Troubleshooting

### Common Issues:

1. **"Connection refused"**
   - Check Redis host/port in secrets
   - Verify Redis service is running

2. **"Auth failed"**
   - Check Redis password in secrets
   - Some Redis instances don't require passwords

3. **"Command limit exceeded"**
   - Upgrade Redis plan
   - Optimize data storage

### Debug Commands:

```python
# Test in Streamlit app
if st.button("Test Redis"):
    test_redis()
```

## Ready to Deploy!

Once Redis is configured:

1. ✅ Push your code to GitHub
2. ✅ Deploy to Streamlit Cloud with Redis secrets
3. ✅ Multiple users can now use your app simultaneously!
4. ✅ All data persists across sessions and deployments

**Your stock analyzer is now production-ready with persistent multi-user support!** 🚀