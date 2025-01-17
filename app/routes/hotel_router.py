from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.controllers.hotel_controller import fetch_and_save_hotels, get_cached_hotels
from pydantic import BaseModel

router = APIRouter()

class FetchHotelsRequest(BaseModel):
    location: str  # Latitude and longitude as a string, e.g., "40.748817,-73.985428"
    radius: int    # Search radius in meters

@router.post("/hotels/fetch")
async def fetch_hotels_route(request: FetchHotelsRequest, db: AsyncSession = Depends(get_db)):
    """
    Fetch hotels from an external API (e.g., Google Places API) and save them to the database.
    """
    try:
        await fetch_and_save_hotels(
            location=request.location,
            radius=request.radius,
            db=db
        )
        return {"message": "Hotels fetched and saved successfully."}
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
