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
| Slack Notifier | Worker integration for real-time alerts |

Backend API is available at: `http://localhost:8001/api/alerts`
Collector endpoint is: `http://localhost:8000/logs`

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

### 🛡️ Browser Extension (Real Traffic)

The preferred way to send logs in this branch is using the **ShadowGuard AI Browser Extension**.

1. Navigate to `chrome://extensions/`.
2. Load the `extension/` folder as an unpacked extension.
3. Configure settings with your Collector URL: `http://localhost:8000/logs`.
4. See `extension/README.md` for full details.

### 🧪 Synthetic Logs (Generator)

The synthetic generator is disabled by default in `docker-compose.yml` to favor real extension logs.

To run it manually on your host:
```bash
python generator/generate_logs.py
```
The generator sends logs to: `http://localhost:8000/logs`

---

### Resetting Alerts (Fresh Demo)

To clear old alerts stored in Redis:

```bash
docker-compose down -v
docker-compose up --build
```

The `-v` flag removes volumes, wiping all stored data.
