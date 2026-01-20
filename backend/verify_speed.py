import asyncio
import time
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.simulation.generator import SimulationGenerator
from backend.models import Base
from backend.database import DATABASE_URL, Base

# Use the real DB for speed test (or SQLite file if not available, but 'memory' is too fast to be realistic)
# We will use SQLite file to simulate disk I/O at least.
TEST_DB_URL = "sqlite+aiosqlite:///./speed_test.db"

async def test_speed():
    print("🏎️  Starting 50,000 Row Speed Test...")
    
    # Setup
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Run Test
    async with async_session() as session:
        generator = SimulationGenerator(session)
        
        start_time = time.time()
        
        # --- THE RACE ---
        run_id, count = await generator.generate_batch()
        # ----------------
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📊 RESULTS:")
        print(f"   Rows Generated:  {count}")
        print(f"   Time Taken:      {duration:.4f} seconds")
        print(f"   Speed:           {count / duration:.0f} rows/sec")
        
        if duration < 10.0:
            print("\n✅ SUCCESS: Generation was under 10 seconds!")
        else:
            print("\n❌ FAILURE: Too slow (> 10s). Optimization needed.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_speed())
