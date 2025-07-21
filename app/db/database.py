from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import keys

DATABASE_URL = keys.neon_db_connection_DATABASE_URL

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create async sessionmaker
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

# Declare Base for models to inherit
Base = declarative_base()

# Dependency to get DB session per request
async def get_db():
    async with SessionLocal() as session:
        yield session
