from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.controllers.tickets_controller import fetch_and_cache_tickets, get_cached_tickets, book_ticket
from pydantic import BaseModel
from app.models.ticket import Ticket
from sqlalchemy.sql import select

router = APIRouter()

@router.get("/tickets")
async def get_tickets(db: AsyncSession = Depends(get_db)):
    """
    Fetch all tickets from the database.
    """
    result = await db.execute(select(Ticket))
    tickets = result.scalars().all()
    return [ticket.to_dict() for ticket in tickets]

class FetchTicketsRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str

@router.post("/tickets/fetch")
async def fetch_tickets_route(request: FetchTicketsRequest, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to fetch tickets from the external API and save them to the database.
    """
    try:
        await fetch_and_cache_tickets(
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            db=db,
        )
        return {"message": "Tickets fetched and saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class BookTicketRequest(BaseModel):
    ticket_id: int

@router.post("/tickets/book")
async def book_ticket_route(request: BookTicketRequest, db: AsyncSession = Depends(get_db)):
    """
    Book a ticket and assign a luggage entry.
    """
    try:
        booking_info = await book_ticket(ticket_id=request.ticket_id, db=db)
        return booking_info
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
