"""
Test script to verify database connection handling improvements
"""
import asyncio
from app.db.database import get_db, engine
from app.db.models import Candidate
from sqlalchemy.future import select
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_connection():
    """Test database connection and query"""
    try:
        async with engine.begin() as conn:
            logger.info("Database connection established successfully")
            
        # Test getting a session
        async for db in get_db():
            logger.info("Database session created successfully")
            
            # Test a simple query
            result = await db.execute(select(Candidate).limit(1))
            candidates = result.scalars().all()
            logger.info(f"Query executed successfully. Found {len(candidates)} candidates.")
            break
            
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_connection())
