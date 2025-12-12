"""
Map seed data script for FlyEase airport navigation.
Run with: python -m app.scripts.seed_map
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import SessionLocal, engine
from app.base import Base
from app.models.location import Location
from app.models.path import Path
from app.models.wall import Wall


# Airport locations - realistic airport layout
LOCATIONS = [
    # Gates
    {"id": 1, "name": "Gate A1", "type": "gate", "category": "departure", "description": "Domestic departures", "coordinates": {"x": 100, "y": 50}},
    {"id": 2, "name": "Gate A2", "type": "gate", "category": "departure", "description": "Domestic departures", "coordinates": {"x": 150, "y": 50}},
    {"id": 3, "name": "Gate A3", "type": "gate", "category": "departure", "description": "Domestic departures", "coordinates": {"x": 200, "y": 50}},
    {"id": 4, "name": "Gate B1", "type": "gate", "category": "international", "description": "International departures", "coordinates": {"x": 300, "y": 50}},
    {"id": 5, "name": "Gate B2", "type": "gate", "category": "international", "description": "International departures", "coordinates": {"x": 350, "y": 50}},
    
    # Check-in counters
    {"id": 6, "name": "Check-in A", "type": "checkin", "category": "service", "description": "Domestic check-in", "coordinates": {"x": 150, "y": 300}},
    {"id": 7, "name": "Check-in B", "type": "checkin", "category": "service", "description": "International check-in", "coordinates": {"x": 300, "y": 300}},
    
    # Security
    {"id": 8, "name": "Security Checkpoint", "type": "security", "category": "service", "description": "TSA security screening", "coordinates": {"x": 225, "y": 200}},
    
    # Amenities
    {"id": 9, "name": "Food Court", "type": "restaurant", "category": "food", "description": "Multiple dining options", "coordinates": {"x": 175, "y": 125}},
    {"id": 10, "name": "Coffee Shop", "type": "restaurant", "category": "food", "description": "Quick coffee and snacks", "coordinates": {"x": 275, "y": 125}},
    {"id": 11, "name": "Duty Free", "type": "shop", "category": "retail", "description": "Tax-free shopping", "coordinates": {"x": 225, "y": 100}},
    {"id": 12, "name": "Restrooms", "type": "restroom", "category": "service", "description": "Public restrooms", "coordinates": {"x": 225, "y": 150}},
    
    # Main areas
    {"id": 13, "name": "Main Entrance", "type": "entrance", "category": "access", "description": "Airport main entrance", "coordinates": {"x": 225, "y": 350}},
    {"id": 14, "name": "Baggage Claim", "type": "baggage", "category": "service", "description": "Luggage pickup area", "coordinates": {"x": 225, "y": 400}},
    {"id": 15, "name": "Information Desk", "type": "info", "category": "service", "description": "Airport information", "coordinates": {"x": 225, "y": 275}},
]

# Paths connecting locations with distances
PATHS = [
    # Main entrance connections
    {"source_id": 13, "destination_id": 14, "distance": 50, "congestion": 1},
    {"source_id": 13, "destination_id": 15, "distance": 75, "congestion": 1},
    {"source_id": 13, "destination_id": 6, "distance": 60, "congestion": 2},
    {"source_id": 13, "destination_id": 7, "distance": 85, "congestion": 2},
    
    # Check-in to security
    {"source_id": 6, "destination_id": 8, "distance": 100, "congestion": 3},
    {"source_id": 7, "destination_id": 8, "distance": 100, "congestion": 3},
    {"source_id": 15, "destination_id": 8, "distance": 75, "congestion": 2},
    
    # Security to gates area
    {"source_id": 8, "destination_id": 9, "distance": 80, "congestion": 2},
    {"source_id": 8, "destination_id": 10, "distance": 80, "congestion": 2},
    {"source_id": 8, "destination_id": 11, "distance": 100, "congestion": 1},
    {"source_id": 8, "destination_id": 12, "distance": 50, "congestion": 1},
    
    # Food/shop to gates
    {"source_id": 9, "destination_id": 1, "distance": 80, "congestion": 1},
    {"source_id": 9, "destination_id": 2, "distance": 60, "congestion": 1},
    {"source_id": 9, "destination_id": 3, "distance": 80, "congestion": 1},
    {"source_id": 10, "destination_id": 4, "distance": 80, "congestion": 1},
    {"source_id": 10, "destination_id": 5, "distance": 60, "congestion": 1},
    {"source_id": 11, "destination_id": 9, "distance": 50, "congestion": 1},
    {"source_id": 11, "destination_id": 10, "distance": 50, "congestion": 1},
    
    # Gate connections
    {"source_id": 1, "destination_id": 2, "distance": 50, "congestion": 1},
    {"source_id": 2, "destination_id": 3, "distance": 50, "congestion": 1},
    {"source_id": 4, "destination_id": 5, "distance": 50, "congestion": 1},
    {"source_id": 3, "destination_id": 11, "distance": 60, "congestion": 1},
    {"source_id": 4, "destination_id": 11, "distance": 80, "congestion": 1},
    
    # Restrooms connections
    {"source_id": 12, "destination_id": 9, "distance": 30, "congestion": 1},
    {"source_id": 12, "destination_id": 10, "distance": 30, "congestion": 1},
]

# Walls for collision detection (obstacles in the airport)
WALLS = [
    # Outer walls
    {"x1": 50, "y1": 25, "x2": 400, "y2": 25},
    {"x1": 50, "y1": 25, "x2": 50, "y2": 425},
    {"x1": 400, "y1": 25, "x2": 400, "y2": 425},
    {"x1": 50, "y1": 425, "x2": 400, "y2": 425},
    
    # Security checkpoint barrier
    {"x1": 100, "y1": 180, "x2": 200, "y2": 180},
    {"x1": 250, "y1": 180, "x2": 350, "y2": 180},
    
    # Gate area dividers
    {"x1": 250, "y1": 25, "x2": 250, "y2": 75},
]


async def seed_map_data():
    """Seed the map with locations, paths, and walls."""
    async with SessionLocal() as db:
        # Clear existing data
        await db.execute(Path.__table__.delete())
        await db.execute(Location.__table__.delete())
        await db.execute(Wall.__table__.delete())
        await db.commit()
        
        # Add locations
        for loc_data in LOCATIONS:
            location = Location(**loc_data)
            db.add(location)
        
        await db.commit()
        print(f"✅ Added {len(LOCATIONS)} locations")
        
        # Add paths (bidirectional)
        path_count = 0
        for path_data in PATHS:
            # Forward path
            db.add(Path(**path_data))
            # Reverse path
            db.add(Path(
                source_id=path_data["destination_id"],
                destination_id=path_data["source_id"],
                distance=path_data["distance"],
                congestion=path_data["congestion"]
            ))
            path_count += 2
        
        await db.commit()
        print(f"✅ Added {path_count} paths (bidirectional)")
        
        # Add walls
        for wall_data in WALLS:
            db.add(Wall(**wall_data))
        
        await db.commit()
        print(f"✅ Added {len(WALLS)} walls")
        
        print("\n🎉 Map seed complete!")


if __name__ == "__main__":
    asyncio.run(seed_map_data())
