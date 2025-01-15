import requests
from fastapi import HTTPException
from sqlalchemy.future import select  # Import `select` here
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ticket import Ticket
from datetime import datetime
import os

BOOKING_API_KEY = os.getenv("BOOKING_API_KEY")  # Retrieve API key from .env
API_URL = "https://sky-scanner3.p.rapidapi.com/flights/search-multi-city"  # API endpoint

async def fetch_and_cache_tickets(origin: str, destination: str, departure_date: str, db: AsyncSession):
    headers = {
        "Content-Type": "application/json",
        "X-RapidAPI-Key": BOOKING_API_KEY,
        "X-RapidAPI-Host": "sky-scanner3.p.rapidapi.com",
    }

    payload = {
        "market": "US",
        "locale": "en-US",
        "currency": "USD",
        "adults": 1,
        "children": 0,
        "infants": 0,
        "cabinClass": "economy",
        "stops": ["direct", "1stop", "2stops"],
        "sort": "cheapest_first",
        "flights": [
            {
                "fromEntityId": origin,
                "toEntityId": destination,
                "departDate": departure_date,
            }
        ],
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch tickets: {response.text}")

    # Parse the JSON response
    try:
        ticket_data = response.json()
    except ValueError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response: {response.text}")

    # Validate the `itineraries` key
    if "data" not in ticket_data or "itineraries" not in ticket_data["data"]:
        raise HTTPException(status_code=500, detail=f"Invalid response structure: {ticket_data}")

    # Extract ticket details and save them
    itineraries = ticket_data["data"]["itineraries"]
    for itinerary in itineraries:
        try:
            # Assuming the first leg of each itinerary represents the main flight
            leg = itinerary["legs"][0]
            new_ticket = Ticket(
                airline_name=leg["carriers"]["marketing"][0]["name"],
                flight_number=leg["segments"][0]["flightNumber"],
                origin=leg["origin"]["id"],
                destination=leg["destination"]["id"],
                departure_time=datetime.fromisoformat(leg["departure"]),
                arrival_time=datetime.fromisoformat(leg["arrival"]),
                price=itinerary["price"]["raw"],
            )
            db.add(new_ticket)
        except Exception as e:
            print(f"Error processing itinerary: {itinerary}, Error: {e}")
            continue

    await db.commit()

async def get_cached_tickets(origin: str, destination: str, departure_date: str, db: AsyncSession):
    stmt = select(Ticket).where(
        Ticket.origin == origin,
        Ticket.destination == destination,
        Ticket.departure_time.like(f"{departure_date}%")
    )
    result = await db.execute(stmt)
    tickets = result.scalars().all()
    return [{"origin": t.origin, "destination": t.destination, "departure_time": t.departure_time,
             "arrival_time": t.arrival_time, "price": t.price, "airline_name": t.airline_name} for t in tickets]