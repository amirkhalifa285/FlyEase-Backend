import heapq    
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.location import Location
from app.models.path import Path
from ..db.database import get_db
from fastapi import HTTPException
from ..models.wall import Wall
import random

SECURITY_AND_CHECKIN_IDS = [59, 39, 38, 60, 61, 37, 34, 33, 32, 31, 30, 29] #for simulating congestion

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

    #readable_path = [location_mapping[loc_id] for loc_id in path]

    return {"path": path, "total_distance": total_distance}


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
    print("Fetched walls:", walls)
    return walls

async def update_congestion(db: AsyncSession):
    # Fetch all paths leading to the specified locations
    query = select(Path).where(Path.destination_id.in_(SECURITY_AND_CHECKIN_IDS))
    result = await db.execute(query)
    paths = result.scalars().all()

    # Update congestion values randomly
    for path in paths:
        path.congestion = random.randint(1, 10)  # Random value between 1 (low) and 10 (high)
        db.add(path)  # Add to session

    await db.commit()

async def calculate_overall_congestion(db: AsyncSession):
    # Calculate the overall congestion level
    query = select(Path).where(Path.destination_id.in_(SECURITY_AND_CHECKIN_IDS))
    result = await db.execute(query)
    paths = result.scalars().all()

    total_congestion = sum(path.congestion for path in paths)
    num_paths = len(paths)
    avg_congestion = total_congestion / num_paths if num_paths > 0 else 0

    # Determine congestion level
    if avg_congestion <= 3:
        return {"level": "Low", "value": avg_congestion}
    elif avg_congestion <= 6:
        return {"level": "Medium", "value": avg_congestion}
    else:
        return {"level": "High", "value": avg_congestion}
    

async def update_and_fetch_congestion(db: AsyncSession):
    # Step 1: Update congestion values
    paths_query = await db.execute(select(Path))
    paths = paths_query.scalars().all()

    import random
    for path in paths:
        path.congestion = random.randint(1, 10)  # Random congestion value between 1 and 10
        db.add(path)  # Add path back to session for update

    await db.commit()  # Commit changes to the database

    # Step 2: Calculate overall congestion level
    total_congestion = sum(path.congestion for path in paths)
    num_paths = len(paths)
    avg_congestion = total_congestion / num_paths if num_paths > 0 else 0

    overall_congestion = {}
    if avg_congestion <= 3:
        overall_congestion = {"level": "Low", "value": avg_congestion}
    elif avg_congestion <= 6:
        overall_congestion = {"level": "Medium", "value": avg_congestion}
    else:
        overall_congestion = {"level": "High", "value": avg_congestion}

    # Step 3: Return updated paths and overall congestion
    updated_paths = [
        {
            "source_id": path.source_id,
            "destination_id": path.destination_id,
            "congestion": path.congestion,
        }
        for path in paths
    ]

    return {**overall_congestion, "paths": updated_paths}