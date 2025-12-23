"""ShadowGuard Dashboard API - Main application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from config import settings
from database import init_database, db_available
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

# Include core routers (always available)
app.include_router(health.router)
app.include_router(alerts.router)
app.include_router(stats.router)
app.include_router(analytics.router)
app.include_router(simulate.router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("=" * 60)
    print("         SHADOWGUARD DASHBOARD API")
    print("=" * 60)
    
    # Try to initialize database (optional - won't crash if fails)
    db_ok = await init_database()
    
    if db_ok:
        # Only register auth routes if database is available
        try:
            from routes import auth
            app.include_router(auth.router)
            print("[AUTH] ✅ Authentication routes enabled")
        except Exception as e:
            print(f"[AUTH] ⚠️  Auth routes disabled: {e}")
    else:
        print("[AUTH] ⚠️  Authentication disabled (no database)")
    
    print("-" * 60)
    print("[API] ✅ Dashboard API ready on port 8001")
    print("-" * 60)
