from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from ..base import Base  # Ensure this imports all models and remains intact

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

# Fetch and modify the database URL for asyncpg compatibility
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

print(f"Loaded DATABASE_URL: {DATABASE_URL}")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Add SSL settings for Heroku compatibility
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"ssl": "require"}  # Enforce SSL for Heroku Postgres
)

SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Dependency for database sessions
async def get_db():
    async with SessionLocal() as session:
        yield session

# Function to create missing tables
async def create_tables():
    async with engine.begin() as conn:
        # Create all missing tables
        await conn.run_sync(Base.metadata.create_all)