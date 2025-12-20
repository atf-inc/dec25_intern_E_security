# dec25_intern_E_security
GitHub Repo for Team E

## Run Locally

This project supports a fast frontend dev loop (Vite HMR) while running the backend pipeline in Docker.

### Prerequisites

- Docker + Docker Compose
- Node.js (npm)
- Python (only if running the generator on host; otherwise, it can run in Docker)

---

### Terminal 1 — Backend (Docker)

From the repo root:

```bash
docker-compose up --build
```

**What this starts (in Docker):**

| Service | Description |
|---------|-------------|
| Redis | Message broker and storage |
| Collector | Log ingestion service |
| Worker | Detection engine + writes alerts to Redis |
| Dashboard API | FastAPI backend |

Backend API is available at: `http://localhost:8001/api/alerts`

---

### Terminal 2 — Frontend (Vite dev server)

```bash
cd dashboard/frontend
npm install
npm run dev
```

Open the URL printed by Vite (typically `http://localhost:3000` or `http://localhost:3001` if port 3000 is in use).

> **Note:** The frontend uses a dev proxy for `/api` to reach the backend API (`localhost:8001`), so the UI works without CORS issues.

---

### Sending Test Logs (Generator)

#### Option A: Generator in Docker Compose
If the generator is included in `docker-compose.yml`, it starts automatically. Watch logs in Terminal 1.

#### Option B: Generator on Host
Run the generator manually, targeting the Collector via the Nginx gateway:

```bash
python generator/generate_logs.py
```

The generator sends logs to: `http://localhost:3000/collect/logs`

---

### Resetting Alerts (Fresh Demo)

To clear old alerts stored in Redis:

```bash
docker-compose down -v
docker-compose up --build
```

The `-v` flag removes volumes, wiping all stored data.
