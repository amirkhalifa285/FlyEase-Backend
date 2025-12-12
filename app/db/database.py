from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from ..base import Base  # Ensure this imports all models and remains intact
from ..core.settings import settings

# Get DATABASE_URL and convert for asyncpg compatibility
DATABASE_URL = settings.DATABASE_URL

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Add SSL settings based on configuration
connect_args = {"ssl": "require"} if settings.SSL_REQUIRED else {}

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for debugging SQL queries
    connect_args=connect_args
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