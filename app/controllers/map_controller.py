import heapq    
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.location import Location
from app.models.path import Path
from ..db.database import get_db
from fastapi import HTTPException
import requests
from ..models.wall import Wall

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
    # Fetch locations
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

    # Fetch paths
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

    # Fetch walls
    walls = await get_walls(db)

    return {"locations": locations, "paths": paths, "walls": walls}

#utility func for walls
def line_segments_intersect(p1, q1, p2, q2):
    """Check if two line segments (p1q1 and p2q2) intersect."""

    def orientation(a, b, c):
        val = (b[1] - a[1]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[1] - b[1])
        if val == 0:
            return 0  # Collinear
        return 1 if val > 0 else 2  # Clockwise or counterclockwise

    def on_segment(a, b, c):
        return (
            min(a[0], b[0]) <= c[0] <= max(a[0], b[0])
            and min(a[1], b[1]) <= c[1] <= max(a[1], b[1])
        )

    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    if o1 != o2 and o3 != o4:
        return True

    # Special cases
    if o1 == 0 and on_segment(p1, q1, p2):
        return True
    if o2 == 0 and on_segment(p1, q1, q2):
        return True
    if o3 == 0 and on_segment(p2, q2, p1):
        return True
    if o4 == 0 and on_segment(p2, q2, q1):
        return True

    return False



async def calculate_shortest_path(source_id: int, destination_id: int, db: AsyncSession):
    

    # Fetch all paths and build the graph
    result = await db.execute(select(Path))
    paths = result.scalars().all()
    graph = {}

    for path in paths:
        graph.setdefault(path.source_id, []).append((path.destination_id, path.distance))
        graph.setdefault(path.destination_id, []).append((path.source_id, path.distance))

    # Fetch all walls
    walls_query = await db.execute(select(Wall))
    walls = walls_query.scalars().all()

    # Utility function to check if a line intersects any wall
    def intersects_wall(x1, y1, x2, y2):
        for wall in walls:
            if line_segments_intersect(
                (x1, y1), (x2, y2), (wall.x1, wall.y1), (wall.x2, wall.y2)
            ):
                return True
        return False

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
                # Get coordinates of the current and neighbor nodes
                curr_location = next(
                    (loc for loc in locations if loc.id == node), None
                )
                neighbor_location = next(
                    (loc for loc in locations if loc.id == neighbor), None
                )
                if curr_location and neighbor_location:
                    x1, y1 = curr_location.coordinates["x"], curr_location.coordinates["y"]
                    x2, y2 = neighbor_location.coordinates["x"], neighbor_location.coordinates["y"]
                    if not intersects_wall(x1, y1, x2, y2):  # Skip paths intersecting walls
                        heapq.heappush(pq, (cost + weight, neighbor, path))

        return None, float("inf")  # No path found

    # Fetch all locations
    locations_query = await db.execute(select(Location))
    locations = locations_query.scalars().all()

    # Calculate shortest path
    path, total_distance = dijkstra(graph, source_id, destination_id)
    if not path:
        return {"error": "No path found"}

    # Fetch human-readable location names
    location_query = await db.execute(select(Location).filter(Location.id.in_(path)))
    location_mapping = {loc.id: loc.name for loc in location_query.scalars()}

    readable_path = [location_mapping[loc_id] for loc_id in path]

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


async def get_walls(db: AsyncSession):
    # Fetch all walls from the database
    walls_query = await db.execute(select(Wall))
    walls = [
        {
            "id": wall.id,
            "x1": wall.x1,
            "y1": wall.y1,
            "x2": wall.x2,
            "y2": wall.y2,
        }
        for wall in walls_query.scalars()
    ]
    return walls