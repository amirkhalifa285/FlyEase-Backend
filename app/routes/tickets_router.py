from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.controllers.tickets_controller import (
    book_ticket,
    get_ticket_with_luggage,
    fetch_all_tickets,
)
from pydantic import BaseModel

router = APIRouter()

class BookTicketRequest(BaseModel):
    ticket_id: int

@router.get("/tickets")
async def get_all_tickets_route(db: AsyncSession = Depends(get_db)):
    """
    Get all tickets.
    """
    try:
        tickets = await fetch_all_tickets(db=db)
        return tickets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tickets: {str(e)}")

@router.post("/tickets/book")
async def book_ticket_route(request: BookTicketRequest, db: AsyncSession = Depends(get_db)):
    """
    Book a ticket and assign a luggage entry.
    """
    try:
        booking_info = await book_ticket(ticket_id=request.ticket_id, db=db)
        return booking_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tickets/{ticket_id}")
async def get_ticket_with_luggage_route(ticket_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get ticket details along with luggage information.
    """
    try:
        ticket_info = await get_ticket_with_luggage(ticket_id=ticket_id, db=db)
        return ticket_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
