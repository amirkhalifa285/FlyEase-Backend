from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.database import get_db
from ..controllers.flight_controller import get_all_flights, create_flight, fetch_and_save_flights,track_flight_by_number

router = APIRouter()

@router.get("/flights")
async def fetch_flights(db: AsyncSession = Depends(get_db)):
    """
    Fetch all flights from the database and return them.
    """
    return await get_all_flights(db)

@router.post("/flights/fetch")
async def fetch_live_flights(db: AsyncSession = Depends(get_db)):
    """
    Fetch live flights from the AviationStack API and save them to the database.
    """
    try:
        await fetch_and_save_flights(db)
        return {"message": "Live flights fetched and saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/flights")
async def add_flight(flight_data: dict, db: AsyncSession = Depends(get_db)):
    """
    Manually add a flight to the database.
    """
    return await create_flight(db, flight_data)

@router.get("/flights/track/{flight_number}")
async def track_flight(flight_number: str, db: AsyncSession = Depends(get_db)):
    """
    Track a flight by its flight number.
    """
    try:
        return await track_flight_by_number(flight_number, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking flight: {str(e)}")