<p align="center">
  <img src="https://img.shields.io/badge/Status-MVP%20Ready-brightgreen?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/Version-1.0.0-blue?style=for-the-badge" alt="Version" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License" />
</p>

<h1 align="center">🛡️ ShadowGuard AI</h1>
<p align="center">
  <strong>Real-Time Shadow AI/IT Detection Platform</strong><br/>
  <em>AI-powered security monitoring for enterprise environments</em>
</p>

---

## 📋 Overview

**ShadowGuard AI** is an enterprise-grade security platform that detects and monitors unauthorized AI tools and Shadow IT usage in real-time. It uses a multi-layer detection engine combining semantic analysis, behavioral analysis, and rule-based detection to identify potential data exfiltration risks.

### 🎯 Key Highlights

- **🧠 AI-Powered Detection** — Semantic similarity analysis using embeddings
- **📊 Real-Time Dashboard** — Live alerts with risk scores and explanations
- **🔌 Browser Extension** — Capture real user browsing activity
- **⚡ Instant Alerts** — Slack notifications for high-risk events
- **🐳 Docker-Ready** — Full containerized deployment

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ShadowGuard AI                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         │                            │                            │
         ▼                            ▼                            ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ Browser Extension│         │   Generator     │         │   Dashboard     │
│  (Real Traffic)  │         │ (Synthetic Logs)│         │  (React + API)  │
└────────┬────────┘         └────────┬────────┘         └────────▲────────┘
         │                            │                            │
         └────────────────┬───────────┘                            │
                          ▼                                        │
                 ┌─────────────────┐                               │
                 │    Collector    │                               │
                 │    (FastAPI)    │                               │
                 └────────┬────────┘                               │
                          │ Redis Pub/Sub                          │
                          ▼                                        │
                 ┌─────────────────┐                               │
                 │     Worker      │                               │
                 │ (Detection Engine)                              │
                 │  ├── Semantic   │                               │
                 │  ├── Behavioral │                               │
                 │  └── Fusion     │───────────────────────────────┘
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Slack Notifier │
                 │ (Real-time Alerts)│
                 └─────────────────┘
```

---

## 📁 Project Structure

```
shadowguard-ai/
├── 📁 collector/              # Log ingestion service (FastAPI)
│   ├── app/                   # API routes and handlers
│   ├── core/                  # Configuration and Redis client
│   ├── models/                # Data models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic
│   ├── main.py                # Application entry point
│   ├── Dockerfile
│   └── requirements.txt
│
├── 📁 worker/                 # Multi-layer detection engine
│   ├── worker.py              # Main event consumer
│   ├── fusion.py              # Risk score fusion algorithm
│   ├── semantic.py            # Semantic similarity analysis
│   ├── behavior.py            # Behavioral anomaly detection
│   ├── rules.py               # Rule-based detection
│   ├── slack_notifier.py      # Slack alert integration
│   ├── Dockerfile
│   └── requirements.txt
│
├── 📁 dashboard/              # Web UI and backend API
│   ├── frontend/              # React 19 + Vite + TailwindCSS v4
│   │   ├── src/
│   │   │   ├── components/    # UI components
│   │   │   ├── pages/         # Page components
│   │   │   └── App.tsx
│   │   ├── package.json
│   │   └── vite.config.ts
│   ├── backend/               # FastAPI backend
│   │   ├── main.py            # API endpoints
│   │   └── requirements.txt
│   ├── nginx.conf             # Reverse proxy configuration
│   ├── start.sh               # Orchestration script
│   └── Dockerfile             # Multi-stage build
│
├── 📁 generator/              # Synthetic log generator
│   ├── generate_logs.py       # Log generation script
│   ├── Dockerfile
│   └── requirements.txt
│
├── 📁 extension/              # Chrome browser extension
│   ├── manifest.json          # MV3 extension manifest
│   ├── background.js          # Service worker
│   ├── content.js             # Content script
│   ├── popup/                 # Extension popup UI
│   ├── options/               # Extension settings page
│   └── icons/
│
├── 📁 config/                 # Shared configuration
│   ├── anchors.json           # Category definitions for semantic analysis
│   ├── blacklist.json         # Blocked domains
│   └── whitelist.json         # Allowed domains
│
├── 📁 docs/                   # Documentation
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── SETUP.md
│
├── docker-compose.yml         # Service orchestration
├── .env.example               # Environment variables template
├── .gitignore
├── TESTING.md
└── README.md
```

---

## 🛠️ Tech Stack

<table>
  <tr>
    <th>Category</th>
    <th>Technology</th>
  </tr>
  <tr>
    <td><strong>Frontend</strong></td>
    <td>
      <img src="https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=white" alt="React" />
      <img src="https://img.shields.io/badge/TypeScript-5.9-3178C6?style=flat&logo=typescript&logoColor=white" alt="TypeScript" />
      <img src="https://img.shields.io/badge/Vite-7-646CFF?style=flat&logo=vite&logoColor=white" alt="Vite" />
      <img src="https://img.shields.io/badge/TailwindCSS-4-06B6D4?style=flat&logo=tailwindcss&logoColor=white" alt="TailwindCSS" />
      <img src="https://img.shields.io/badge/Framer_Motion-12-0055FF?style=flat&logo=framer&logoColor=white" alt="Framer Motion" />
    </td>
  </tr>
  <tr>
    <td><strong>Backend</strong></td>
    <td>
      <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white" alt="Python" />
      <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI" />
      <img src="https://img.shields.io/badge/Uvicorn-ASGI-499848?style=flat&logoColor=white" alt="Uvicorn" />
    </td>
  </tr>
  <tr>
    <td><strong>Database</strong></td>
    <td>
      <img src="https://img.shields.io/badge/Redis-7-DC382D?style=flat&logo=redis&logoColor=white" alt="Redis" />
    </td>
  </tr>
  <tr>
    <td><strong>AI/ML</strong></td>
    <td>
      <img src="https://img.shields.io/badge/OpenRouter-API-7B61FF?style=flat&logoColor=white" alt="OpenRouter" />
      <img src="https://img.shields.io/badge/Gemini-API-4285F4?style=flat&logo=google&logoColor=white" alt="Gemini" />
      <img src="https://img.shields.io/badge/NumPy-Embeddings-013243?style=flat&logo=numpy&logoColor=white" alt="NumPy" />
    </td>
  </tr>
  <tr>
    <td><strong>Infrastructure</strong></td>
    <td>
      <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white" alt="Docker" />
      <img src="https://img.shields.io/badge/Nginx-Gateway-009639?style=flat&logo=nginx&logoColor=white" alt="Nginx" />
    </td>
  </tr>
  <tr>
    <td><strong>Extension</strong></td>
    <td>
      <img src="https://img.shields.io/badge/Chrome_MV3-Extension-4285F4?style=flat&logo=googlechrome&logoColor=white" alt="Chrome Extension" />
    </td>
  </tr>
</table>

---

## ✨ Features

### 🔍 Multi-Layer Detection Engine

| Layer | Description |
|-------|-------------|
| **Semantic Analysis** | Uses AI embeddings to detect category matches (Generative AI, File Storage, Anonymous Services, etc.) |
| **Behavioral Analysis** | Tracks user patterns and flags anomalies (first-time access, unusual upload volumes) |
| **Rule-Based Detection** | Configurable whitelist/blacklist for immediate allow/block decisions |
| **Fusion Engine** | Combines all signals with intent-aware scoring (POST/PUT uploads weighted differently than GET) |

### 📊 Real-Time Dashboard

- **Live Alert Feed** — Real-time security events with risk scores
- **Alert Simulation** — Test scenarios for demo purposes
- **Risk Level Indicators** — CRITICAL, HIGH, MEDIUM, LOW, SAFE
- **AI-Generated Explanations** — Powered by Gemini API
- **Responsive Design** — Modern glassmorphism UI with animations

### 🔌 Browser Extension

- **Passive Monitoring** — Captures browsing activity without user intervention
- **Configurable Endpoint** — Point to any collector instance
- **Privacy-Focused** — Only sends metadata, not page content
- **Chrome MV3** — Built on the latest manifest version

### 🔔 Notifications

- **Slack Integration** — Real-time alerts to security team channels
- **Threshold-Based** — Only notify on HIGH/CRITICAL events

---

## 🚀 Quick Start

### Prerequisites

- **Docker** + **Docker Compose**
- **Node.js** (v18+) — for frontend development
- **Python 3.11** — for local development
- API keys (optional but recommended):
  - `OPENROUTER_API_KEY` — For semantic embeddings
  - `GEMINI_API_KEY` — For AI-generated explanations

### 1️⃣ Clone & Configure

```bash
git clone https://github.com/your-org/shadowguard-ai.git
cd shadowguard-ai

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 2️⃣ Start All Services (Docker)

```bash
docker-compose up --build
```

This starts:
| Service | Port | Description |
|---------|------|-------------|
| Redis | 6379 | Message broker & data store |
| Collector | Internal | Log ingestion (accessible via dashboard) |
| Worker | 8000 | Detection engine |
| Dashboard | 3000 | UI + API gateway |

### 3️⃣ Access the Dashboard

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4️⃣ Generate Test Alerts

**Option A: Use the Browser Extension (Recommended)**

1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" → Select the `extension/` folder
4. Configure the collector URL: `http://localhost:3000/logs`
5. Browse the web normally — events are captured automatically

**Option B: Synthetic Logs**

```bash
python generator/generate_logs.py \
  --url http://localhost:3000/logs \
  --type mixed \
  --num-logs 50 \
  --once
```

---

## ⚙️ Environment Configuration

Create a `.env` file at the project root:

```env
# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Service Ports
COLLECTOR_PORT=8000
DASHBOARD_PORT=3000

# AI/ML APIs (optional but recommended)
OPENROUTER_API_KEY=your_openrouter_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Self-hosted Embedding Model (alternative to OpenRouter)
EMBEDDING_API_URL=http://YOUR_VM_IP:8000/embed
```

### API Keys

| Key | Purpose | Required |
|-----|---------|----------|
| `OPENROUTER_API_KEY` | Semantic embeddings for domain categorization | Optional (falls back to keyword matching) |
| `GEMINI_API_KEY` | AI-generated alert explanations | Optional (shows "AI explanation unavailable" if missing) |
| `EMBEDDING_API_URL` | Self-hosted embedding model endpoint | Optional (alternative to OpenRouter) |

---

## 🧪 Development

### Hybrid Mode (Recommended for Frontend Dev)

**Terminal 1 — Backend Services (Docker)**
```bash
docker-compose up redis collector worker
```

**Terminal 2 — Frontend (Vite HMR)**
```bash
cd dashboard/frontend
npm install
npm run dev
```

Access at: [http://localhost:3000](http://localhost:3000) (with hot reload)

### Full Local Development

**Collector:**
```bash
cd collector
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Worker:**
```bash
cd worker
pip install -r requirements.txt
python worker.py
```

**Dashboard Backend:**
```bash
cd dashboard/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

**Dashboard Frontend:**
```bash
cd dashboard/frontend
npm install
npm run dev
```

---

## 🔄 API Endpoints

### Dashboard API (`http://localhost:3000/api/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check with Redis status |
| GET | `/api/alerts` | Fetch security alerts |
| GET | `/api/users` | Get user statistics |

### Collector API (Internal, proxied through dashboard)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/logs` | Ingest log events |
| GET | `/logs?params` | Ingest via query params (for proxies) |
| GET | `/health` | Collector health check |

---

## 🔧 Operations

### Reset All Data

```bash
docker-compose down -v
docker-compose up --build
```

The `-v` flag removes volumes, wiping all stored alerts.

### View Service Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f worker
```

### Health Checks

```bash
# Dashboard API
curl http://localhost:3000/api/health

# Collector (via proxy)
curl http://localhost:3000/health
```



