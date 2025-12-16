# Dashboard Service

The Dashboard service provides a web-based UI for monitoring Shadow IT detections. It displays real-time alerts, risk scores, and allows security analysts to review and manage detected events.

## Architecture

- **Frontend:** React 19 + Vite + TailwindCSS v4
- **Backend:** FastAPI (Python 3.11)
- **Deployment:** Multi-stage Docker build with Nginx reverse proxy

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
├── Dockerfile         # Multi-stage build
├── nginx.conf         # Reverse proxy config
└── start.sh          # Service orchestration
```

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
docker-compose up
```

The dashboard will be accessible at **http://localhost:8000**

### How It Works
- Nginx listens on port 3000
- Static frontend files served from `/usr/share/nginx/html`
- API requests (`/api/*`) proxied to FastAPI backend on port 8000
- Redis connection via Docker network (`redis:6379`)

## API Endpoints

- `GET /` - Health check
- `GET /api/health` - Service health + Redis status
- `GET /api/alerts` - Fetch alerts from Redis
- `/collect/*` - Collector service integration

## Environment Variables

Set in `docker-compose.yml`:
- `REDIS_HOST` - Redis hostname (default: `redis`)
- `REDIS_PORT` - Redis port (default: `6379`)
