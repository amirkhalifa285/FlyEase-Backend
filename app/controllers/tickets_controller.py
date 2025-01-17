import requests
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ticket import Ticket
from app.models.luggage import Luggage
from app.models.flight import Flight
from datetime import datetime
import os

BOOKING_API_KEY = os.getenv("BOOKING_API_KEY")
API_URL = "https://sky-scanner3.p.rapidapi.com/flights/search-multi-city"

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

    try:
        ticket_data = response.json()
    except ValueError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response: {response.text}")

    if "data" not in ticket_data or "itineraries" not in ticket_data["data"]:
        raise HTTPException(status_code=500, detail=f"Invalid response structure: {ticket_data}")

    itineraries = ticket_data["data"]["itineraries"]
    for itinerary in itineraries:
        try:
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

async def book_ticket(ticket_id: int, db: AsyncSession):
    """
    Book a ticket, assign a luggage entry, and save flight details to the flights table.
    """
    ticket_result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = ticket_result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    if ticket.luggage_id:
        raise HTTPException(status_code=400, detail="Ticket already booked with luggage.")

    new_luggage = Luggage(
        weight=20.0,
        status="Checked-in",
        last_location="Unknown"
    )
    db.add(new_luggage)
    await db.flush()

    ticket.luggage_id = new_luggage.luggage_id

    new_flight = Flight(
        airline_name=ticket.airline_name,
        flight_number=ticket.flight_number,
        origin=ticket.origin,
        destination=ticket.destination,
        departure_time=ticket.departure_time,
        arrival_time=ticket.arrival_time,
        status="Booked"
    )
    db.add(new_flight)

    await db.commit()
    await db.refresh(ticket)

    return {
        "message": "Ticket booked successfully.",
        "flight_number": ticket.flight_number,
        "luggage_id": new_luggage.luggage_id
    }