import requests
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ticket import Ticket
from app.models.luggage import Luggage
from app.models.flight import Flight
from ..models.users import User
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

async def book_ticket(ticket_id: int, db: AsyncSession, current_user: User):
    """
    Book a ticket, assign a luggage entry, and save flight details to the flights table.
    """
    # Fetch the ticket
    ticket_result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = ticket_result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    if ticket.user_id:
        raise HTTPException(status_code=400, detail="Ticket already booked.")

    # Assign a luggage entry
    new_luggage = Luggage(
        weight=20.0,
        status="Checked-in",
        last_location="Unknown"
    )
    db.add(new_luggage)
    await db.flush()  # Ensures luggage ID is generated

    # Update the ticket's user_id and luggage_id
    ticket.user_id = current_user.id
    ticket.luggage_id = new_luggage.luggage_id

    # Save flight details to the flights table
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

    # Commit the changes
    await db.commit()
    await db.refresh(ticket)

    return {
        "message": "Ticket booked successfully.",
        "flight_number": ticket.flight_number,
        "luggage_id": new_luggage.luggage_id
    }


async def track_luggage_by_id(luggage_id: int, db: AsyncSession):
    """
    Fetch luggage details using the luggage ID.
    """
    luggage_result = await db.execute(select(Luggage).where(Luggage.luggage_id == luggage_id))
    luggage = luggage_result.scalar_one_or_none()

    if not luggage:
        raise HTTPException(status_code=404, detail="Luggage not found.")

    return {
        "luggage_id": luggage.luggage_id,
        "weight": luggage.weight,
        "status": luggage.status,
        "last_location": luggage.last_location,
    }

async def fetch_user_tickets(db: AsyncSession, user_id: int):
    """
    Fetch tickets for a specific user asynchronously.
    :param db: Async database session
    :param user_id: ID of the user whose tickets need to be fetched
    :return: JSON response with user tickets or a message if no tickets found
    """
    query = select(Ticket).filter(Ticket.user_id == user_id)
    result = await db.execute(query)
    tickets = result.scalars().all()
    
    if not tickets:
        return {"message": "No tickets found for the current user"}
    
    return {"tickets": [ticket.to_dict() for ticket in tickets]}