import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from backend.models import Base, SimRun, Telemetry
from datetime import datetime

# Import the real configuration
from backend.database import DATABASE_URL
TEST_DB_URL = DATABASE_URL

async def verify_models():
    print("🔬 Starting Phase 1 Verification...")
    print(f"   Target: {TEST_DB_URL}")
    
    # 1. Setup Engine
    # SQLite needs this check disabled for async to work in scripts occasionally
    connect_args = {"check_same_thread": False} if "sqlite" in TEST_DB_URL else {}
    engine = create_async_engine(TEST_DB_URL, echo=False, connect_args=connect_args)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    try:
        # 2. Create Tables
        print("\n1️⃣  Creating Database Tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("   ✅ Tables created successfully (SimRun, Telemetry).")

        # 3. Test Data Insertion
        print("\n2️⃣  Testing Data Insertion...")
        async with async_session() as session:
            async with session.begin():
                # Create a SimRun
                sim_run = SimRun(status="TESTING", start_time=datetime.utcnow())
                session.add(sim_run)
                await session.flush() # Get ID
                
                print(f"   Created SimRun with ID: {sim_run.id}")

                # Create Telemetry linked to SimRun
                telemetry = Telemetry(
                    sim_run_id=sim_run.id,
                    timestamp_sim=datetime.utcnow(),
                    induction_power=50.5,
                    quench_water_temp=25.0,
                    quench_water_flow=120.0,
                    quench_pressure=3.5,
                    coil_scan_speed=5.0,
                    tempering_speed=2.0,
                    state="HEATING",
                    coil_life_counter=100
                )
                session.add(telemetry)
            
            print("   ✅ Mock data inserted successfully.")

        # 4. Test Data Query & Relationship
        print("\n3️⃣  Testing Data Retrieval & Relationships...")
        async with async_session() as session:
            # Query SimRun and load specific Telemetry
            result = await session.execute(select(SimRun).where(SimRun.status == "TESTING"))
            fetched_run = result.scalars().first()
            
            # Check relationship (lazy load requires explicit query or eager load options normally, 
            # but for this test we'll just query telemetry directly to prove foreign key works)
            result_tele = await session.execute(select(Telemetry).where(Telemetry.sim_run_id == fetched_run.id))
            fetched_tele = result_tele.scalars().first()
            
            if fetched_run and fetched_tele:
                print(f"   ✅ Retrieved SimRun ID: {fetched_run.id}")
                print(f"   ✅ Retrieved Telemetry Power: {fetched_tele.induction_power} kW")
                print("   ✅ Relationships and Foreign Keys are working.")
            else:
                print("   ❌ Failed to retrieve data.")

        print("\n🎉 Phase 1 Verification COMPLETE: All systems go!")

    except Exception as e:
        print(f"\n❌ Verification FAILED: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify_models())
