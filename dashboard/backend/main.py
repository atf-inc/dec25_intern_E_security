"""ShadowGuard Dashboard API - Main application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from config import settings
from routes import health, alerts, stats, analytics, simulate, auth

app = FastAPI(title="ShadowGuard Dashboard API")

# Session Middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include core routers
app.include_router(health.router)
app.include_router(alerts.router)
app.include_router(stats.router)
app.include_router(analytics.router)
app.include_router(simulate.router)
app.include_router(auth.router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("=" * 60)
    print("         SHADOWGUARD DASHBOARD API")
    print("=" * 60)
    print("[API] ✅ Dashboard API ready on port 8001")

    print("-" * 60)

