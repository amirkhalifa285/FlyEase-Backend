import requests
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.hotel import Hotel
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
API_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

def geocode_address(address: str):
    """
    Convert a text-based address (like 'London') into (lat, lng) using Google Geocoding API.
    """
    GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": API_KEY,
    }
    response = requests.get(GEOCODE_URL, params=params)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to geocode address: {response.text}"
        )

    data = response.json()
    # Check for a successful geocoding response
    if data.get("status") != "OK":
        raise HTTPException(
            status_code=400,
            detail=f"Geocoding error: {data.get('status')}. Response: {data}"
        )

    results = data.get("results")
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No geocoding results found for: {address}"
        )

    # Take the first matching result
    geometry = results[0]["geometry"]
    lat = geometry["location"]["lat"]
    lng = geometry["location"]["lng"]
    return lat, lng

def is_latlng(location_str: str) -> bool:
    """
    Simple check to see if 'location_str' looks like lat,lng.
    We'll try to split and parse as floats.
    """
    parts = location_str.split(',')
    if len(parts) == 2:
        try:
            float(parts[0])
            float(parts[1])
            return True
        except ValueError:
            pass
    return False

async def fetch_dynamic_hotels(location: str, radius: int):
    """
    Fetch hotels dynamically from Google Places API based on a location.
    'location' can be:
      - A text-based place (e.g. "London")
      - A coordinate string (e.g. "40.748817,-73.985428")
    We'll geocode if it's not obviously lat,lng.
    """
    if not is_latlng(location):
        # If the user typed a city name, geocode it
        lat, lng = geocode_address(location)
        location = f"{lat},{lng}"
    # Now 'location' should be "lat,lng" for the Google Places call
    
    params = {
        "location": location,
        "radius": radius,
        "type": "lodging",
        "key": API_KEY,
    }

    response = requests.get(API_URL, params=params)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to fetch hotels: {response.text}"
        )

    try:
        hotel_data = response.json()
    except ValueError:
        raise HTTPException(
            status_code=500,
            detail="Invalid JSON response from Google API"
        )

    if "results" not in hotel_data:
        raise HTTPException(
            status_code=500,
            detail="Invalid response structure from Google Places"
        )

    hotels = hotel_data["results"][:25]  # Limit to 25
    processed_hotels = []

    for hotel in hotels:
        photos = hotel.get("photos", [])
        photo_url = (
            f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400"
            f"&photoreference={photos[0].get('photo_reference')}&key={API_KEY}"
        ) if photos else "https://via.placeholder.com/400x300?text=No+Image+Available"

        processed_hotels.append({
            "name": hotel["name"],
            "address": hotel.get("vicinity", ""),
            "rating": hotel.get("rating"),
            "total_ratings": hotel.get("user_ratings_total"),
            "photo_reference": photo_url,
            "open_now": hotel.get("opening_hours", {}).get("open_now"),
        })

    return processed_hotels

async def get_cached_hotels(db: AsyncSession):
    """
    Retrieve all hotels from the database and generate full image URLs for the photo_reference.
    """
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Securely load API key
    BASE_PHOTO_URL = "https://maps.googleapis.com/maps/api/place/photo"

    stmt = select(Hotel)
    result = await db.execute(stmt)
    hotels = result.scalars().all()

    hotel_list = []
    for hotel in hotels:
        hotel_dict = hotel.to_dict()
        if hotel_dict["photo_reference"]:
            # Generate full photo URL
            hotel_dict["photo_reference"] = (
                f"{BASE_PHOTO_URL}?maxwidth=400"
                f"&photoreference={hotel_dict['photo_reference']}"
                f"&key={GOOGLE_API_KEY}"
            )
        else:
            # Fallback if there's no photo reference
            hotel_dict["photo_reference"] = "https://via.placeholder.com/400x300?text=No+Image+Available"
        hotel_list.append(hotel_dict)

    return hotel_list
