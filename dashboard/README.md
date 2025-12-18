# Dashboard Service

The Dashboard service provides a web-based UI for monitoring Shadow IT detections. It displays real-time alerts, risk scores, and allows security analysts to review and manage detected events.

## Architecture

- **Frontend:** React 19 + Vite + TailwindCSS v4
- **Backend:** FastAPI (Python 3.11)
- **Web Server:** Nginx (single-gateway configuration)
- **Deployment:** Multi-stage Docker build with integrated orchestration

## Structure

```
dashboard/
├── frontend/           # React application
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── backend/           # FastAPI application
│   ├── main.py
│   ├── config.py
│   └── requirements.txt
├── Dockerfile         # Multi-stage build (Node.js + Python)
├── nginx.conf         # Single-gateway reverse proxy configuration
└── start.sh          # Service orchestration script
```

## Port Configuration

### Production-Ready Single-Gateway Architecture

**Port 3000** - **ONLY** public entry point (served by Nginx)
- **Dashboard UI:** `http://localhost:3000`
- **API Backend:** `http://localhost:3000/api/*` → proxied to internal port 8001
- **Collector Logs:** `http://localhost:3000/logs` → proxied to collector service
- **Collector Ingest:** `http://localhost:3000/collect/*` → proxied to collector service

**Port 8001** - Internal FastAPI backend (not exposed externally)
- Only accessible within Docker container
- Handles `/api/*` requests from Nginx

**Port 8000** - ❌ **NOT EXPOSED** (collector internal only)
- Collector runs on port 8000 inside Docker network
- Accessible to dashboard container via `shadowguard-collector:8000`
- Not accessible from host machine

### Why Single Gateway?

✅ **One entry point** - All traffic flows through port 3000  
✅ **No CORS issues** - Same origin for UI and API  
✅ **Clean routing** - Nginx handles all proxying internally  
✅ **Production-ready** - Maps directly to port 443 in production  
✅ **Security** - Collector not exposed to public network  

### Local Development

- Frontend dev server: `http://localhost:5173` (Vite)
- Backend dev server: `http://localhost:8001` (Uvicorn)

## Development (Local)

### Frontend
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
# Runs on http://localhost:8001
```

## Docker Deployment

### Build Image
```bash
docker build -t shadowguard-dashboard .
```

### Run with Docker Compose
```bash
# From project root
docker-compose up dashboard

# With all services
docker-compose up redis collector worker dashboard

# Rebuild after changes
docker-compose up --build dashboard
```

### Access Points
- **Dashboard UI:** http://localhost:3000
- **API Endpoints:** http://localhost:3000/api/*
- **Log Ingestion:** http://localhost:3000/logs (for generator)

## How It Works

The dashboard uses a multi-stage Docker build and single Nginx gateway configuration:

1. **Frontend Build (Stage 1)**
   - Node.js 20 builds React app with Vite
   - Output: Static files in `dist/`

2. **Backend Preparation (Stage 2)**
   - Python 3.11 installs FastAPI dependencies
   - Prepares backend application

3. **Runtime Container (Stage 3)**
   - Nginx serves static frontend on port 3000
   - Nginx proxies API requests to internal port 8001
   - Nginx proxies collector requests to `shadowguard-collector:8000`
   - FastAPI backend runs on internal port 8001
   - All services orchestrated via `start.sh`

### Network Flow (Production-Ready Single Gateway)

```
┌─────────────────────────────────────────────────────────────┐
│                     Port 3000 (ONLY Public Entry)           │
│                         Nginx Gateway                       │
└─────────────────────────────────────────────────────────────┘
                              |
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   Static Files          /api/*               /logs, /collect/*
   (React UI)         (Dashboard API)         (Collector API)
        │                     │                     │
        │                     ▼                     ▼
        │            Port 8001 (Internal)    shadowguard-collector:8000
        │            FastAPI Backend         (Docker Network Only)
        │                     │
        │                     ▼
        └────────────────► Redis
```

**Key Points:**
- Browser → `http://localhost:3000` → Gets React UI
- UI → `http://localhost:3000/api/alerts` → Nginx proxies to backend port 8001
- Backend → Redis → Fetches alerts
- Generator → `http://localhost:3000/logs` → Nginx proxies to collector
- Collector service NOT accessible directly from host

## API Endpoints

All endpoints accessed via `http://localhost:3000`

### Dashboard Backend API
- `GET /api/health` - Service health + Redis connectivity status
- `GET /api/alerts` - Fetch security alerts from Redis
- `GET /api/users` - Get user statistics

### Collector Endpoints (Proxied through Nginx)
- `POST /logs` - Log ingestion endpoint (used by generator)
- `GET /logs?params` - Log ingestion via GET (used by proxies)
- `POST /collect/ingest` - Alternative ingestion endpoint

## Environment Variables

Set in `docker-compose.yml`:
- `REDIS_HOST` - Redis hostname (default: `redis`)
- `REDIS_PORT` - Redis port (default: `6379`)
- `DASHBOARD_PORT` - Public port (default: `3000`)
- ~~`API_GATEWAY_PORT`~~ - **REMOVED** (single gateway only)

## Running the Generator

With the new single-gateway architecture, the generator must use port 3000:

```bash
# ✅ Correct (new single-gateway)
python generator/generate_logs.py --url http://localhost:3000/logs --once --num-logs 50

# ❌ Wrong (old dual-gateway - no longer works)
python generator/generate_logs.py --url http://localhost:8000/logs
```

## Health Checks

The container includes automatic health monitoring:
```bash
curl -f http://localhost:3000/api/health
```

Health check runs every 30 seconds with a 40-second startup grace period.

## Architectural Benefits

### Before (Dual Gateway - Problematic)
```
Port 3000: UI + API
Port 8000: API + Collector  ← Confusion & duplication
```

### After (Single Gateway - Production-Ready)
```
Port 3000: UI + API + Collector  ← Clean & predictable
Port 8000: NOT exposed          ← Secure & internal only
```

**Why This Matters:**
1. **Predictable behavior** - One source of truth
2. **No routing confusion** - Updates work everywhere
3. **CORS eliminated** - Same origin for all requests
4. **Production mapping** - Maps cleanly to HTTPS/443
5. **Security** - Internal services not exposed

## Troubleshooting

### Generator fails to connect
**Old command (fails):**
```bash
python generator/generate_logs.py --url http://localhost:8000/logs
# Error: Connection timeout (port not exposed)
```

**New command (works):**
```bash
python generator/generate_logs.py --url http://localhost:3000/logs
```

### Dashboard shows no alerts
1. Check all services are running:
   ```bash
   docker compose ps
   ```
2. Verify worker is processing events:
   ```bash
   docker logs shadowguard-worker --tail 20
   ```
3. Test log ingestion:
   ```bash
   curl "http://localhost:3000/logs?user_id=test&domain=example.com&url=/test&method=GET&upload_size_bytes=1000"
   ```

### Port 8000 connection timeout
This is **expected behavior** in the new architecture. Port 8000 is no longer exposed to the host. All traffic must go through port 3000.
