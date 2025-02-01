from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.flight import Flight
import requests
import os
from datetime import datetime
from fastapi import HTTPException
API_KEY = os.getenv("FLIGHTS_API_KEY") 
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
        "dep_iata": dep_iata,  
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
        departure_time = datetime.fromisoformat(departure_time).replace(tzinfo=None)  
        arrival_time = datetime.fromisoformat(arrival_time).replace(tzinfo=None)      

        existing_flight = await db.execute(
            select(Flight).where(Flight.flight_number == flight["flight"]["iata"])
        )
        if existing_flight.scalar():
            continue

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


async def track_flight_by_number(flight_number: str, db: AsyncSession):
    """
    Fetch flight details using the flight number.
    """
    flight_result = await db.execute(select(Flight).where(Flight.flight_number == flight_number))
    flight = flight_result.scalar_one_or_none()

    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found.")

    return {
        "flight_number": flight.flight_number,
        "airline_name": flight.airline_name,
        "origin": flight.origin,
        "destination": flight.destination,
        "departure_time": flight.departure_time,
        "arrival_time": flight.arrival_time,
        "status": flight.status,
    }

