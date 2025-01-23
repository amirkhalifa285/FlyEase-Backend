from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.controllers.tickets_controller import fetch_and_cache_tickets, get_cached_tickets, book_ticket, track_luggage_by_id, fetch_user_tickets
from pydantic import BaseModel
from app.models.ticket import Ticket
from app.models.users import User
from ..auth.auth_utils import get_current_user

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
async def book_ticket_route(
    request: BookTicketRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Add current_user dependency
):
    """
    Book a ticket and assign a luggage entry, associating it with the logged-in user.
    """
    try:
        # Pass current_user to associate the ticket with the logged-in user
        booking_info = await book_ticket(ticket_id=request.ticket_id, db=db, current_user=current_user)
        return booking_info
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    
    
@router.get("/luggage/track/{luggage_id}")
async def track_luggage(luggage_id: int, db: AsyncSession = Depends(get_db)):
    """
    Track luggage by its ID.
    """
    try:
        return await track_luggage_by_id(luggage_id, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking luggage: {str(e)}")    
    

@router.get("/my-tickets", tags=["Tickets"])
async def get_my_tickets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch tickets for the currently authenticated user.
    """
    try:
        # Query tickets directly using user_id
        result = await db.execute(
            select(Ticket).where(Ticket.user_id == current_user.id)
        )
        tickets = result.scalars().all()
        return {"tickets": [ticket.to_dict() for ticket in tickets]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tickets: {str(e)}")