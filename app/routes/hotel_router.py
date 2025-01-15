from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.database import get_db
from ..controllers.hotel_controller import fetch_and_save_hotels
from sqlalchemy.future import select
from ..models.hotel import Hotel
from ..auth.amadeus_auth import get_amadeus_access_token


router = APIRouter()

@router.post("/hotels/fetch")
async def fetch_hotels(
    city_code: str = Query(..., description="The IATA city code to fetch hotels for"),
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch hotels by city code using Amadeus API and save them to the database.
    """
    try:
        # Fetch the access token from the token manager
        access_token = get_amadeus_access_token()

        # Call the controller function to fetch hotels
        await fetch_and_save_hotels(db, city_code, limit, offset, access_token)

        return {"message": "Hotels fetched and saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching hotels: {str(e)}")

@router.get("/hotels")
async def get_hotels(page: int = 1, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """
    Fetch hotels from the database for the frontend.
    """
    try:
        # Query hotels from the database with pagination
        hotels_query = await db.execute(
            select(Hotel).offset((page - 1) * limit).limit(limit)
        )
        hotels = hotels_query.scalars().all()
        return hotels
    except Exception as e:
        # Raise HTTPException for better error handling
        raise HTTPException(status_code=500, detail=f"Error fetching hotels from database: {str(e)}")
