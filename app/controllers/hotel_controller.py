import requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.hotel import Hotel
from ..auth.amadeus_auth import get_amadeus_access_token

HOTELS_BY_CITY_URL = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"

async def fetch_and_save_hotels(db: AsyncSession, city_code: str, limit: int, offset: int, access_token: str):
    """
    Fetch hotels using Amadeus Hotel List API and save them to the database.
    """
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        params = {
            "cityCode": city_code,
            "page[limit]": limit,
            "page[offset]": offset,
        }

        response = requests.get(HOTELS_BY_CITY_URL, headers=headers, params=params)
        if response.status_code != 200:
            print("Error Response:", response.text)
            raise Exception(f"Failed to fetch hotels: {response.text}")

        hotels_data = response.json().get("data", [])
        print(f"Fetched {len(hotels_data)} hotels.")

        # Save hotels to the database
        for hotel in hotels_data:
            existing_hotel = await db.execute(select(Hotel).where(Hotel.hotel_id == hotel["hotelId"]))
            if existing_hotel.scalar():
                continue

            new_hotel = Hotel(
                hotel_id=hotel["hotelId"],
                name=hotel["name"],
                chain_code=hotel.get("chainCode", "Unknown"),
                iata_code=hotel.get("iataCode", "Unknown"),
                location=hotel.get("address", {}).get("countryCode", "Unknown"),
                latitude=hotel.get("geoCode", {}).get("latitude"),
                longitude=hotel.get("geoCode", {}).get("longitude"),
                last_update=hotel.get("last_update", None),
            )
            db.add(new_hotel)

        await db.commit()
        print("Hotels saved successfully.")
    except Exception as e:
        print(f"Error fetching hotels: {str(e)}")
        raise Exception(f"Error fetching hotels: {str(e)}")
