"""
Ticket controller for flight search, caching, and booking.
Uses async HTTP calls with timeout and demo mode support.
"""
import httpx
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, cast, Date
from app.models.ticket import Ticket
from app.models.luggage import Luggage
from app.models.flight import Flight
from ..models.users import User
from ..core.settings import settings
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

# API Configuration
API_URL = "https://sky-scanner3.p.rapidapi.com/flights/search-multi-city"
REQUEST_TIMEOUT = 30.0  # seconds

# Demo mode stub data
DEMO_TICKETS = [
    {
        "airline_name": "Demo Airways",
        "flight_number": "DA101",
        "origin": "JFK",
        "destination": "LAX",
        "departure_time": "2024-12-20T08:00:00",
        "arrival_time": "2024-12-20T11:30:00",
        "price": 299.99
    },
    {
        "airline_name": "FlyEase Demo",
        "flight_number": "FE202",
        "origin": "JFK",
        "destination": "LAX",
        "departure_time": "2024-12-20T14:00:00",
        "arrival_time": "2024-12-20T17:30:00",
        "price": 349.99
    },
    {
        "airline_name": "Demo Express",
        "flight_number": "DX303",
        "origin": "JFK",
        "destination": "LAX",
        "departure_time": "2024-12-20T20:00:00",
        "arrival_time": "2024-12-20T23:30:00",
        "price": 279.99
    },
]


async def fetch_and_cache_tickets(origin: str, destination: str, departure_date: str, db: AsyncSession):
    """
    Fetch tickets from SkyScanner API or return demo data if API key is missing.
    Uses async HTTP with timeout and proper error handling.
    """
    # Check for demo mode
    if settings.is_demo_mode or not settings.BOOKING_API_KEY:
        logger.info("Demo mode: returning stub ticket data")
        return _get_demo_tickets(origin, destination, departure_date)
    
    headers = {
        "Content-Type": "application/json",
        "X-RapidAPI-Key": settings.BOOKING_API_KEY,
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

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
    except httpx.TimeoutException:
        logger.error(f"Timeout fetching tickets for {origin} -> {destination}")
        raise HTTPException(status_code=504, detail="Flight search timed out. Please try again.")
    except httpx.HTTPStatusError as e:
        logger.error(f"API error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to fetch tickets: {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Network error fetching tickets: {e}")
        raise HTTPException(status_code=503, detail="Flight search service unavailable. Please try again later.")

    try:
        ticket_data = response.json()
    except ValueError:
        raise HTTPException(status_code=500, detail="Invalid response from flight search API")

    if "data" not in ticket_data or "itineraries" not in ticket_data.get("data", {}):
        logger.warning(f"Unexpected API response structure: {ticket_data}")
        raise HTTPException(status_code=500, detail="Invalid response structure from flight search")

    # Process and cache itineraries
    itineraries = ticket_data["data"]["itineraries"]
    added_count = 0
    
    for itinerary in itineraries:
        try:
            leg = itinerary["legs"][0]
            flight_number = leg["segments"][0]["flightNumber"]
            dep_time = datetime.fromisoformat(leg["departure"].replace("Z", "+00:00"))
            
            # Check for existing ticket to avoid duplicates
            existing = await db.execute(
                select(Ticket).where(
                    Ticket.flight_number == flight_number,
                    cast(Ticket.departure_time, Date) == dep_time.date()
                )
            )
            if existing.scalar_one_or_none():
                continue  # Skip duplicate
            
            new_ticket = Ticket(
                airline_name=leg["carriers"]["marketing"][0]["name"],
                flight_number=flight_number,
                origin=leg["origin"]["id"],
                destination=leg["destination"]["id"],
                departure_time=dep_time,
                arrival_time=datetime.fromisoformat(leg["arrival"].replace("Z", "+00:00")),
                price=itinerary["price"]["raw"],
            )
            db.add(new_ticket)
            added_count += 1
        except (KeyError, IndexError) as e:
            logger.warning(f"Error processing itinerary: {e}")
            continue

    await db.commit()
    logger.info(f"Cached {added_count} new tickets for {origin} -> {destination} on {departure_date}")


def _get_demo_tickets(origin: str, destination: str, departure_date: str) -> list:
    """Return demo tickets with the requested route."""
    return [
        {
            **ticket,
            "origin": origin,
            "destination": destination,
            "departure_time": f"{departure_date}T{ticket['departure_time'].split('T')[1]}",
            "arrival_time": f"{departure_date}T{ticket['arrival_time'].split('T')[1]}",
        }
        for ticket in DEMO_TICKETS
    ]

async def get_cached_tickets(origin: str, destination: str, departure_date: str, db: AsyncSession):
    """Get cached tickets with proper date filtering."""
    try:
        target_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    stmt = select(Ticket).where(
        Ticket.origin == origin,
        Ticket.destination == destination,
        cast(Ticket.departure_time, Date) == target_date
    )
    result = await db.execute(stmt)
    tickets = result.scalars().all()
    
    return [
        {
            "id": t.id,
            "origin": t.origin,
            "destination": t.destination,
            "departure_time": t.departure_time.isoformat() if t.departure_time else None,
            "arrival_time": t.arrival_time.isoformat() if t.arrival_time else None,
            "price": t.price,
            "airline_name": t.airline_name,
            "flight_number": t.flight_number,
        }
        for t in tickets
    ]

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