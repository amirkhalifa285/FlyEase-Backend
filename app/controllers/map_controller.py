from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.location import Location
from app.models.path import Path

async def populate_mock_map(db: AsyncSession):
    # Add sample locations
    locations = [
        {"name": "Gate A1", "type": "gate", "coordinates": {"x": 0, "y": 0}},
        {"name": "Gate A2", "type": "gate", "coordinates": {"x": 5, "y": 0}},
        {"name": "Security Checkpoint", "type": "security", "coordinates": {"x": 10, "y": 5}},
        {"name": "Lounge", "type": "lounge", "coordinates": {"x": 15, "y": 5}},
    ]

    # Insert locations into the database
    for loc in locations:
        location = Location(**loc)
        db.add(location)
    await db.commit()

    # Fetch IDs for locations
    result = await db.execute(select(Location))
    loc_ids = {loc.name: loc.id for loc in result.scalars().all()}

    # Add sample paths
    paths = [
        {"source_id": loc_ids["Gate A1"], "destination_id": loc_ids["Gate A2"], "distance": 5},
        {"source_id": loc_ids["Gate A2"], "destination_id": loc_ids["Security Checkpoint"], "distance": 7},
        {"source_id": loc_ids["Security Checkpoint"], "destination_id": loc_ids["Lounge"], "distance": 5},
    ]

    # Insert paths into the database
    for path in paths:
        db.add(Path(**path))
    await db.commit()


async def get_map_data(db: AsyncSession):
    # Fetch all locations
    locations = await db.execute(select(Location))
    locations_data = [
        {"id": loc.id, "name": loc.name, "type": loc.type, "coordinates": loc.coordinates}
        for loc in locations.scalars()
    ]

    # Fetch all paths
    paths = await db.execute(select(Path))
    paths_data = [
        {"id": path.id, "source_id": path.source_id, "destination_id": path.destination_id, "distance": path.distance}
        for path in paths.scalars()
    ]

    return {"locations": locations_data, "paths": paths_data}
