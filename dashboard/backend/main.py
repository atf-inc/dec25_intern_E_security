"""ShadowGuard Dashboard API - Main application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routes import health, alerts, stats, analytics, simulate

app = FastAPI(title="ShadowGuard Dashboard API")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(alerts.router)
app.include_router(stats.router)
app.include_router(analytics.router)
app.include_router(simulate.router)

