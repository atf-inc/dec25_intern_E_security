# Worker Service

The Worker service is the core detection engine of ShadowGuard AI. It consumes events from Redis, applies multi-layer analysis (rule-based, semantic, behavioral), and generates risk scores using a fusion algorithm.

## Files

- `semantic.py` - **Semantic similarity analysis engine with Redis consumer**
  - Analyzes domains using OpenRouter embeddings
  - Supports both test mode (hardcoded domains) and live mode (Redis events)
  - Subscribes to `events` channel for real-time processing
- `behavior.py` - Behavioral analysis for anomaly detection
- `fusion.py` - Risk score fusion combining all detection layers
- `embedding_cache.json` - Cached category embeddings for performance

## Semantic Analysis (`semantic.py`)

### Features

- **Redis Consumer**: Subscribes to the `events` channel from collector
- **Dual Mode Operation**:
  - **Test Mode** (default): Uses hardcoded domains for offline testing
  - **Live Mode** (`--live` flag): Consumes real-time events from collector
- **Embedding-based Analysis**: Uses OpenRouter API for semantic similarity
- **Offline Fallback**: Automatic fallback to keyword matching if API fails
- **Embedding Cache**: Pre-computed category vectors for fast startup

### Usage

#### Test Mode (Offline)
```bash
python worker/semantic.py
```
Analyzes hardcoded sample domains without requiring Redis or collector.

#### Live Mode (Production)
```bash
python worker/semantic.py --live
```
Connects to Redis and processes real-time events from the collector.

### Redis Integration

**Connection**:
- Host: `localhost` (configurable via `REDIS_HOST` env var)
- Port: `6379` (configurable via `REDIS_PORT` env var)
- Channel: `events` (pub/sub)

**Event Format** (consumed from collector):
```json
{
    "ts": "2025-12-15T10:47:45Z",
    "user_id": "alice@company.com",
    "domain": "claude.ai",
    "url": "/api/v1/chat",
    "method": "POST",
    "upload_size_bytes": 5242880
}
```


**Analysis Output**:
```
📨 New Event Received:
   User: alice@company.com
   Domain: claude.ai
   Upload Size: 5242880 bytes

🔍 Semantic Analysis:
   Top Category  : generative_ai
   Risk Score    : 0.90
   Explanation   : High-confidence AI service (0.94)
   Similarities  :
     - generative_ai       : 0.94
     - file_storage        : 0.75
     - anonymous_services  : 0.90
```

## Complete Pipeline Flow

```
Generator → Collector → Redis → Worker/Semantic
            (HTTP)      (Pub/Sub)  (Subscriber)
```

### Running the Complete Pipeline

1. **Start Redis & Collector**:
```bash
docker-compose up -d redis collector
```

2. **Start Semantic Worker** (in terminal 1):
```bash
python worker/semantic.py --live
```

3. **Generate Logs** (in terminal 2):
```bash
python generator/generate_logs.py --url http://localhost:8000/logs --num-logs 50
```

4. **Observe real-time analysis** in terminal 1

### Stopping the Pipeline
```bash
# Ctrl+C in both terminals
docker-compose down
```

## Environment Variables

- `REDIS_HOST`: Redis server hostname (default: `localhost`)
- `REDIS_PORT`: Redis server port (default: `6379`)
- `OPENROUTER_API_KEY`: OpenRouter API key (optional, falls back to offline mode)

## Risk Categories

1. **Generative AI** (Risk: 0.9)
   - ChatGPT, Claude, Bard, Midjourney
   
2. **File Storage** (Risk: 0.2)
   - Dropbox, Google Drive, OneDrive, Box

3. **Anonymous Services** (Risk: 0.6)
   - ProtonMail, Tutanota, TempMail

## Dependencies

- `redis` - Redis client for pub/sub
- `requests` - HTTP client for OpenRouter API
- `numpy` - Vector similarity calculations
- `python-dotenv` - Environment configuration
