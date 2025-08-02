from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.config import keys
import logging
import asyncio

logger = logging.getLogger(__name__)

DATABASE_URL = keys.neon_db_connection_DATABASE_URL

# Create async engine with connection pooling and retry configuration
if keys.is_local():
    # For local development, use NullPool (no connection pooling)
    engine = create_async_engine(
        DATABASE_URL, 
        echo=True,
        pool_pre_ping=True,  # Validates connections before use
        poolclass=NullPool
    )
else:
    # For production, use proper connection pooling
    engine = create_async_engine(
        DATABASE_URL, 
        echo=True,
        pool_pre_ping=True,  # Validates connections before use
        pool_recycle=3600,   # Recycle connections every hour
        pool_timeout=30,     # Timeout for getting connection from pool
        max_overflow=10,     # Max connections beyond pool_size
        pool_size=5,         # Base number of connections to maintain
    )

# Create async sessionmaker
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

# Declare Base for models to inherit
Base = declarative_base()

# Dependency to get DB session per request with retry logic
async def get_db():
    retries = 3
    for attempt in range(retries):
        try:
            async with SessionLocal() as session:
                yield session
                break
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            if attempt == retries - 1:
                logger.error("All database connection attempts failed")
                raise
            await asyncio.sleep(1)  # Wait 1 second before retry
