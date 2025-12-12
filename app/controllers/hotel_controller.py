"""
Hotel controller for location-based hotel search.
Uses async HTTP calls with timeout and demo mode support.
"""
import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert
from app.models.hotel import Hotel
from app.core.settings import settings
import logging

logger = logging.getLogger(__name__)

# API Configuration
API_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
REQUEST_TIMEOUT = 15.0  # seconds

# Demo mode stub data
DEMO_HOTELS = [
    {
        "name": "FlyEase Demo Hotel",
        "address": "123 Demo Street",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "rating": 4.5,
        "total_ratings": 1250,
        "place_id": "demo_hotel_1",
        "photo_reference": None,
        "open_now": True,
    },
    {
        "name": "Airport Inn Demo",
        "address": "456 Terminal Ave",
        "latitude": 40.7589,
        "longitude": -73.9851,
        "rating": 4.2,
        "total_ratings": 890,
        "place_id": "demo_hotel_2",
        "photo_reference": None,
        "open_now": True,
    },
    {
        "name": "Sky Lounge Hotel",
        "address": "789 Aviation Blvd",
        "latitude": 40.6892,
        "longitude": -74.0445,
        "rating": 4.8,
        "total_ratings": 2100,
        "place_id": "demo_hotel_3",
        "photo_reference": None,
        "open_now": False,
    },
]


async def geocode_address(address: str) -> tuple[float, float]:
    """
    Convert a text-based address into (lat, lng) using Google Geocoding API.
    Returns demo coordinates in demo mode.
    """
    if settings.is_demo_mode or not settings.GOOGLE_API_KEY:
        logger.info("Demo mode: returning default NYC coordinates")
        return (40.7128, -74.0060)
    
    params = {
        "address": address,
        "key": settings.GOOGLE_API_KEY,
    }
    
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(GEOCODE_URL, params=params)
            response.raise_for_status()
    except httpx.TimeoutException:
        logger.error(f"Timeout geocoding address: {address}")
        raise HTTPException(status_code=504, detail="Geocoding timed out. Please try again.")
    except httpx.RequestError as e:
        logger.error(f"Network error during geocoding: {e}")
        raise HTTPException(status_code=503, detail="Geocoding service unavailable")

    data = response.json()
    
    if data.get("status") != "OK":
        raise HTTPException(
            status_code=400,
            detail=f"Geocoding error: {data.get('status')}"
        )

    results = data.get("results", [])
    if not results:
        raise HTTPException(status_code=404, detail=f"No results found for: {address}")

    geometry = results[0]["geometry"]
    return (geometry["location"]["lat"], geometry["location"]["lng"])


def is_latlng(location_str: str) -> bool:
    """Check if location_str looks like lat,lng coordinates."""
    parts = location_str.split(',')
    if len(parts) == 2:
        try:
            float(parts[0])
            float(parts[1])
            return True
        except ValueError:
            pass
    return False


async def fetch_dynamic_hotels(location: str, radius: int, db: AsyncSession = None):
    """
    Fetch hotels from Google Places API or return demo data.
    Optionally caches results to database with upsert.
    """
    # Check for demo mode
    if settings.is_demo_mode or not settings.GOOGLE_API_KEY:
        logger.info("Demo mode: returning stub hotel data")
        return _get_demo_hotels()
    
    # Geocode if needed
    if not is_latlng(location):
        lat, lng = await geocode_address(location)
        location = f"{lat},{lng}"
    
    params = {
        "location": location,
        "radius": radius,
        "type": "lodging",
        "key": settings.GOOGLE_API_KEY,
    }

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(API_URL, params=params)
            response.raise_for_status()
    except httpx.TimeoutException:
        logger.error(f"Timeout fetching hotels for {location}")
        raise HTTPException(status_code=504, detail="Hotel search timed out. Please try again.")
    except httpx.RequestError as e:
        logger.error(f"Network error fetching hotels: {e}")
        raise HTTPException(status_code=503, detail="Hotel search service unavailable")

    try:
        hotel_data = response.json()
    except ValueError:
        raise HTTPException(status_code=500, detail="Invalid response from hotel search API")

    if "results" not in hotel_data:
        raise HTTPException(status_code=500, detail="Invalid response structure from Google Places")

    hotels = hotel_data["results"][:25]  # Limit to 25
    processed_hotels = []

    for hotel in hotels:
        photos = hotel.get("photos", [])
        photo_ref = photos[0].get("photo_reference") if photos else None
        
        hotel_entry = {
            "name": hotel["name"],
            "address": hotel.get("vicinity", ""),
            "latitude": hotel["geometry"]["location"]["lat"],
            "longitude": hotel["geometry"]["location"]["lng"],
            "rating": hotel.get("rating"),
            "total_ratings": hotel.get("user_ratings_total"),
            "place_id": hotel["place_id"],
            "photo_reference": photo_ref,
            "open_now": hotel.get("opening_hours", {}).get("open_now"),
        }
        processed_hotels.append(hotel_entry)
        
        # Upsert to database if session provided
        if db:
            await _upsert_hotel(db, hotel_entry)
    
    if db:
        await db.commit()
        logger.info(f"Cached {len(processed_hotels)} hotels for {location}")

    # Add photo URLs to response
    return [_add_photo_url(h) for h in processed_hotels]


async def _upsert_hotel(db: AsyncSession, hotel_data: dict):
    """Upsert a hotel by place_id."""
    stmt = insert(Hotel).values(**hotel_data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["place_id"],
        set_={k: v for k, v in hotel_data.items() if k != "place_id"}
    )
    await db.execute(stmt)


def _add_photo_url(hotel: dict) -> dict:
    """Add full photo URL to hotel dict."""
    if hotel.get("photo_reference") and settings.GOOGLE_API_KEY:
        hotel["photo_url"] = (
            f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400"
            f"&photoreference={hotel['photo_reference']}&key={settings.GOOGLE_API_KEY}"
        )
    else:
        hotel["photo_url"] = "https://via.placeholder.com/400x300?text=No+Image+Available"
    return hotel


def _get_demo_hotels() -> list:
    """Return demo hotels with placeholder images."""
    return [
        {
            **hotel,
            "photo_url": "https://via.placeholder.com/400x300?text=Demo+Hotel"
        }
        for hotel in DEMO_HOTELS
    ]


async def get_cached_hotels(db: AsyncSession):
    """Retrieve all cached hotels from database with photo URLs."""
    stmt = select(Hotel)
    result = await db.execute(stmt)
    hotels = result.scalars().all()

    return [
        _add_photo_url({
            "id": hotel.id,
            "name": hotel.name,
            "address": hotel.address,
            "latitude": hotel.latitude,
            "longitude": hotel.longitude,
            "rating": hotel.rating,
            "total_ratings": hotel.total_ratings,
            "place_id": hotel.place_id,
            "photo_reference": hotel.photo_reference,
            "open_now": hotel.open_now,
        })
        for hotel in hotels
    ]

