"""ShadowGuard Dashboard API - Main application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routes import health, alerts, stats, analytics, simulate

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

# Include routers
app.include_router(health.router)
app.include_router(alerts.router)
app.include_router(stats.router)
app.include_router(analytics.router)
app.include_router(auth.router)

@app.on_event("startup")
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
app.include_router(simulate.router)

