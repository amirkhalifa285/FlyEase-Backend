from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.controllers.hotel_controller import fetch_dynamic_hotels, get_cached_hotels
from pydantic import BaseModel

router = APIRouter()

class FetchHotelsRequest(BaseModel):
    location: str  # e.g. "40.748817,-73.985428" OR "London"
    radius: int    # Search radius in meters

@router.post("/hotels/fetch")
async def fetch_hotels_route(request: FetchHotelsRequest):
    """
    Fetch hotels dynamically from the Google Places API (in-memory only).
    """
    try:
        hotels = await fetch_dynamic_hotels(
            location=request.location,
            radius=request.radius,
        )
        return hotels
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hotels")
async def get_hotels(db: AsyncSession = Depends(get_db)):
    """
    Fetch all cached hotels from the database.
    """
    try:
        hotels = await get_cached_hotels(db)
        return hotels
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))