import asyncio
from sqlalchemy import select, func
from backend.database import AsyncSessionLocal
from backend.models import Telemetry, SimRun

async def verify_data():
    async with AsyncSessionLocal() as session:
        # 1. Verify SimRun
        run_res = await session.execute(select(SimRun).where(SimRun.id == 1))
        run = run_res.scalar()
        if run:
            print(f"✅ SimRun(id=1) FOUND. Status: {run.status}")
        else:
            print("❌ SimRun(id=1) NOT FOUND. Data storage will fail.")
            return

        # 2. Count Total Rows
        result = await session.execute(select(func.count(Telemetry.id)))
        count = result.scalar()
        print(f"📊 Total Telemetry Rows: {count}")
        
        if count > 0:
            # 3. Show Last 3 Rows to see progression
            print("\n📝 LAST 3 RECORDS:")
            result = await session.execute(select(Telemetry).order_by(Telemetry.id.desc()).limit(3))
            rows = result.scalars().all()
            
            for row in rows:
                print(f"ID: {row.id} | Time: {row.timestamp_sim} | State: {row.state}")
                print(f"   part_id: {row.part_id} | OK: {row.ok_count} | NG: {row.ng_count}")
                print("-" * 40)
        else:
            print("\n⚠️ NO TELEMETRY DATA YET. (Please run a cycle in the UI first)")

if __name__ == "__main__":
    asyncio.run(verify_data())
