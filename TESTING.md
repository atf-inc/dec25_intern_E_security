# End-to-End Testing Guide

This guide describes how to verify the full flow of the ShadowGuard system: Generator -> Collector -> Redis -> Worker -> Dashboard.

## 1. Start Services

### Redis
Ensure Redis is running (via Docker):
```bash
docker run -d -p 6379:6379 redis
```

### Unified Backend (Collector + Dashboard)
In a new terminal (start from **Project Root**):
```bash
# This runs BOTH the Collector (for /logs) and Dashboard API (for /api/alerts) on port 8000
uvicorn dashboard.backend.main:app --port 8000 --reload
```
Runs on `http://localhost:8000`.

### Dashboard Frontend
In a new terminal:
```bash
cd dashboard/frontend
npm run dev
```
Runs on `http://localhost:5173`.

### Worker
In a new terminal:
```bash
cd worker
python worker.py
```

## 2. Generate Test Traffic

Run the generator (sends to `http://localhost:8000/logs`):

In a new terminal:
```bash
cd generator
python generate_logs.py --verbose --num-logs 20 --delay 0.5
```

## 3. Verification

### Console Output
- **Generator**: Should show "Sent: X success".
- **Unified Backend**: Should show `POST /logs` requests AND `/ws/alerts` connections.
- **Worker**: Should capture events, print `[PROCESSED]`, and push alerts to Redis.

### Dashboard UI
- Open `http://localhost:5173`.
- Verify alerts appear in the live feed.
