import asyncio
from sqlalchemy import select, func
from backend.database import AsyncSessionLocal
from backend.models import SimRun

async def verify_sim_runs():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count(SimRun.id)))
        count = result.scalar()
        print(f"📊 Total SimRun Rows: {count}")

if __name__ == "__main__":
    asyncio.run(verify_sim_runs())
