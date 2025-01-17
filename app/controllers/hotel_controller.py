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

async def fetch_and_save_hotels(location: str, radius: int, db: AsyncSession):
    """
    Fetch hotels from Google Places API and save them to the database.
    """
    params = {
        "location": location,
        "radius": radius,
        "type": "lodging",
        "key": API_KEY,
    }

    response = requests.get(API_URL, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch hotels: {response.text}")

    try:
        hotel_data = response.json()
    except ValueError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response: {response.text}")

    if "results" not in hotel_data:
        raise HTTPException(status_code=500, detail=f"Invalid response structure: {hotel_data}")

    hotels = hotel_data["results"][:25]
    for hotel in hotels:
        try:
            new_hotel = Hotel(
                name=hotel["name"],
                address=hotel.get("vicinity", ""),
                latitude=hotel["geometry"]["location"]["lat"],
                longitude=hotel["geometry"]["location"]["lng"],
                rating=hotel.get("rating"),
                total_ratings=hotel.get("user_ratings_total"),
                place_id=hotel["place_id"],
                photo_reference=hotel.get("photos", [{}])[0].get("photo_reference"),
                open_now=hotel.get("opening_hours", {}).get("open_now")
            )
            db.add(new_hotel)
        except Exception as e:
            print(f"Error processing hotel: {hotel}, Error: {e}")
            continue

    await db.commit()

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
            hotel_dict["photo_reference"] = f"{BASE_PHOTO_URL}?maxwidth=400&photoreference={hotel_dict['photo_reference']}&key={GOOGLE_API_KEY}"
        else:
            # Fallback for missing photos
            hotel_dict["photo_reference"] = "https://via.placeholder.com/400x300?text=No+Image+Available"
        hotel_list.append(hotel_dict)

    return hotel_list

