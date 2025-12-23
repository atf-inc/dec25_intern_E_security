from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings
import urllib.parse

def fix_database_url_for_asyncpg(db_url: str) -> tuple[str, dict]:
    """
    Fix database URL for asyncpg compatibility by removing unsupported parameters
    and converting them to appropriate connect_args.
    
    Args:
        db_url: The original database URL
        
    Returns:
        Tuple of (fixed_url, connect_args)
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
        # Remove from URL params
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

# Fix the database URL and get connect_args
db_url, connect_args = fix_database_url_for_asyncpg(settings.DATABASE_URL)

# Create Async Engine with proper configuration
engine = create_async_engine(
    db_url,
    connect_args=connect_args,
    echo=settings.ENVIRONMENT == "development",  # Only show SQL in development
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_timeout=30,
)

# Create Session Factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
async def get_db():
    """Database session dependency for FastAPI"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()