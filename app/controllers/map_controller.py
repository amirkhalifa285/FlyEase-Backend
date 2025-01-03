import heapq    
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.location import Location
from app.models.path import Path
from ..db.database import get_db
from fastapi import HTTPException
import requests

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
    locations_query = await db.execute(select(Location))
    locations = [
        {
            "id": loc.id,
            "name": loc.name,
            "type": loc.type,
            "category": loc.category,
            "coordinates": loc.coordinates,
        }
        for loc in locations_query.scalars()
    ]

    # Fetch all paths
    paths_query = await db.execute(select(Path))
    paths = [
        {
            "id": path.id,
            "source_id": path.source_id,
            "destination_id": path.destination_id,
            "distance": path.distance,
        }
        for path in paths_query.scalars()
    ]

    return {"locations": locations, "paths": paths}

async def calculate_shortest_path(source_id: int, destination_id: int, db: AsyncSession):
    from sqlalchemy.future import select
    from app.models.location import Location
    from app.models.path import Path
    import heapq

    # Fetch all paths and build the graph
    result = await db.execute(select(Path))
    paths = result.scalars().all()
    graph = {}

    for path in paths:
        graph.setdefault(path.source_id, []).append((path.destination_id, path.distance))
        graph.setdefault(path.destination_id, []).append((path.source_id, path.distance))

    # Implement Dijkstra's Algorithm
    def dijkstra(graph, start, end):
        pq = [(0, start, [])]  # Priority queue: (cost, current_node, path)
        visited = set()

        while pq:
            cost, node, path = heapq.heappop(pq)
            if node in visited:
                continue
            path = path + [node]
            if node == end:
                return path, cost
            visited.add(node)
            for neighbor, weight in graph.get(node, []):
                heapq.heappush(pq, (cost + weight, neighbor, path))

        return None, float("inf")  # No path found

    # Calculate shortest path
    path, total_distance = dijkstra(graph, source_id, destination_id)
    if not path:
        return {"error": "No path found"}

    # Fetch human-readable location names
    location_query = await db.execute(select(Location).filter(Location.id.in_(path)))
    locations = {loc.id: loc.name for loc in location_query.scalars()}

    # Map IDs to names in the path
    readable_path = [locations[loc_id] for loc_id in path]

    return {"path": readable_path, "total_distance": total_distance}


""" (class) AsyncSession
Asyncio version of _orm.Session.

The _asyncio.AsyncSession is a proxy for a traditional
_orm.Session instance.

The _asyncio.AsyncSession is **not safe for use in concurrent
tasks.**. See session_faq_threadsafe for background.

To use an _asyncio.AsyncSession with custom _orm.Session implementations, see the
_asyncio.AsyncSession.sync_session_class parameter. """

#admin permission
async def add_location(location_data: dict, db: AsyncSession):
    new_location = Location(**location_data)
    db.add(new_location)
    await db.commit()
    await db.refresh(new_location)
    return new_location

async def add_path(path_data: dict, db: AsyncSession):
    new_path = Path(**path_data)
    db.add(new_path)
    await db.commit()
    await db.refresh(new_path)
    return new_path

async def update_location(location_id: int, location_data: dict, db: AsyncSession):
    query = await db.execute(select(Location).filter(Location.id == location_id))
    location = query.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found.")
    for key, value in location_data.items():
        setattr(location, key, value)
    db.add(location)
    await db.commit()
    await db.refresh(location)
    return location

async def delete_location(location_id: int, db: AsyncSession):
    query = await db.execute(select(Location).filter(Location.id == location_id))
    location = query.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found.")
    await db.delete(location)
    await db.commit()
    return {"message": "Location deleted successfully."}


