from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import Interview
from datetime import datetime

async def create_interview(session: AsyncSession, candidate_id: int, score: float, summary: str):
    new_interview = Interview(
        candidate_id=candidate_id,
        score=score,
        summary=summary,
        date=datetime.utcnow()
    )
    session.add(new_interview)
    await session.commit()
    await session.refresh(new_interview)
    return new_interview


if __name__ == "__main__":
    print("hello")
#     from db.crud import create_interview

# # Inside some API or handler
#     await create_interview(session=db, candidate_id=1, score=92.0, summary="Excellent in data structures.")
