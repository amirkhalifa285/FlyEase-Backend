from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.flight import Flight
import requests
import os
from datetime import datetime

API_KEY = os.getenv("FLIGHTS_API_KEY")  # Load the API key from the .env file
BASE_URL = "http://api.aviationstack.com/v1/flights"

async def get_all_flights(db: AsyncSession):
    """
    Retrieve all flights from the database.
    """
    result = await db.execute(select(Flight))
    return result.scalars().all()

async def create_flight(db: AsyncSession, flight_data: dict):
    """
    Add a new flight to the database.
    """
    new_flight = Flight(**flight_data)
    db.add(new_flight)
    await db.commit()
    await db.refresh(new_flight)
    return new_flight

async def fetch_and_save_flights(db: AsyncSession, dep_iata: str = "TLV", limit: int = 30):
    """
    Fetch live flight data from the AviationStack API and save it to the database.
    """
    params = {
        "access_key": API_KEY,
        "dep_iata": dep_iata,  # Replace with your airport's IATA code (e.g., TLV for Ben Gurion Airport)
        "limit": limit,
    }

    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch flights: {response.status_code}")

    data = response.json().get("data", [])
    for flight in data:
        departure_time = flight["departure"]["scheduled"]
        arrival_time = flight["arrival"]["scheduled"]

        # Skip flights with missing data
        if not departure_time or not arrival_time:
            continue

        # Convert ISO timestamps to Python datetime objects
        departure_time = datetime.fromisoformat(departure_time).replace(tzinfo=None)  # Make timezone-naive
        arrival_time = datetime.fromisoformat(arrival_time).replace(tzinfo=None)      # Make timezone-naive

        # Check if the flight already exists in the database
        existing_flight = await db.execute(
            select(Flight).where(Flight.flight_number == flight["flight"]["iata"])
        )
        if existing_flight.scalar():
            continue

        # Create a new flight entry
        new_flight = Flight(
            airline_name=flight["airline"]["name"],
            flight_number=flight["flight"]["iata"],
            origin=flight["departure"]["airport"],
            destination=flight["arrival"]["airport"],
            departure_time=departure_time,
            arrival_time=arrival_time,
            status=flight["flight_status"],
        )
        db.add(new_flight)

    await db.commit()






# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from ..models.flight import Flight

# async def get_all_flights(db: AsyncSession):
#     result = await db.execute(select(Flight))
#     return result.scalars().all()

# async def create_flight(db: AsyncSession, flight_data: dict):
#     new_flight = Flight(**flight_data)
#     db.add(new_flight)
#     await db.commit()
#     await db.refresh(new_flight)
#     return new_flight
