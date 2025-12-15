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