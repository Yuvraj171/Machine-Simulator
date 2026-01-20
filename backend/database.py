import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Get DB URL from env, default to example if not set (for safety in dev)
# Note: In production, ensure DATABASE_URL is set correctly.
# Get DB URL from env, default to SQLite for local dev if not set
# Use absolute path to ensure scripts and server (uvicorn) access the same file regardless of CWD
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "simulation_v2.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DB_PATH}")

# Create Async Engine
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_async_engine(
    DATABASE_URL,
    echo=True, # Set to False in production
    connect_args=connect_args,
    future=True
)

# Atomic Session Maker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Base Model for ORM
Base = declarative_base()

# Dependency for FastAPI Routers
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
