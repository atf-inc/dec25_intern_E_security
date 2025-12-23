"""
Database configuration with optional PostgreSQL support.
If PostgreSQL is not available, the app continues without auth features.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings
import urllib.parse

# Global state for database availability
_engine = None
_async_session_local = None
db_available = False

# Base class for models (always available for imports)
Base = declarative_base()


def fix_database_url_for_asyncpg(db_url: str) -> tuple[str, dict]:
    """
    Fix database URL for asyncpg compatibility by removing unsupported parameters
    and converting them to appropriate connect_args.
    """
    connect_args = {}
    
    # Parse the URL
    parsed = urllib.parse.urlparse(db_url)
    qs = urllib.parse.parse_qs(parsed.query)
    
    # Handle sslmode - asyncpg uses ssl in connect_args instead of URL parameter
    if "sslmode" in qs:
        sslmode = qs["sslmode"][0]
        if sslmode == "require":
            connect_args["ssl"] = "require"
        elif sslmode == "prefer":
            connect_args["ssl"] = "prefer"
        elif sslmode == "disable":
            connect_args["ssl"] = False
        del qs["sslmode"]
    
    # Remove channel_binding - not supported by asyncpg at all
    if "channel_binding" in qs:
        del qs["channel_binding"]
    
    # Remove any other asyncpg-incompatible parameters
    incompatible_params = ["gssencmode", "krbsrvname", "gsslib", "service"]
    for param in incompatible_params:
        if param in qs:
            del qs[param]
    
    # Reconstruct URL without unsupported parameters
    new_query = urllib.parse.urlencode(qs, doseq=True)
    parsed = parsed._replace(query=new_query)
    clean_url = urllib.parse.urlunparse(parsed)

    # Ensure we use asyncpg driver
    if clean_url.startswith("postgresql://"):
        clean_url = clean_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif clean_url.startswith("postgres://"):
        clean_url = clean_url.replace("postgres://", "postgresql+asyncpg://", 1)
    
    return clean_url, connect_args


async def init_database():
    """
    Initialize database connection. Call this on startup.
    Returns True if successful, False otherwise.
    """
    global _engine, _async_session_local, db_available
    
    try:
        db_url, connect_args = fix_database_url_for_asyncpg(settings.DATABASE_URL)
        
        _engine = create_async_engine(
            db_url,
            connect_args=connect_args,
            echo=settings.ENVIRONMENT == "development",
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_timeout=30,
        )
        
        # Test connection
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        _async_session_local = sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        db_available = True
        print("[DB] ✅ Database connected and tables initialized")
        return True
        
    except Exception as e:
        print(f"[DB] ⚠️  Database unavailable: {e}")
        print("[DB] ⚠️  Auth features disabled - app will continue without database")
        db_available = False
        return False


def get_engine():
    """Get the database engine (may be None if database unavailable)."""
    return _engine


async def get_db():
    """Database session dependency for FastAPI."""
    if not db_available or _async_session_local is None:
        # Return None - routes should handle this gracefully
        yield None
        return
        
    async with _async_session_local() as session:
        try:
            yield session
        finally:
            await session.close()