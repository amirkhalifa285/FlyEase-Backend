import asyncio
from app.db.database import get_db, engine
from app.controllers.map_controller import populate_mock_map

async def run_populate():
    # Create a new database connection
    async with engine.begin() as conn:
        # Use the async generator to get the database session
        async for db in get_db():
            await populate_mock_map(db)

if __name__ == "__main__":
    asyncio.run(run_populate())
