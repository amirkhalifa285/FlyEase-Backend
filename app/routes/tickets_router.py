from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.controllers.tickets_controller import fetch_and_cache_tickets, get_cached_tickets
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

# Fetch tickets from the external API and cache them in the database
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