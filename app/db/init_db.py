import asyncio
from app.db.database import engine, Base

from app.db import models

async def init_models():
    async with engine.begin() as conn:
        print("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)

    print("Database reset complete!")

if __name__ == "__main__":
    asyncio.run(init_models())
