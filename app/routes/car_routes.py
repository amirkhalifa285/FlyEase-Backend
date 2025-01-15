from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.database import get_db
from ..controllers.car_controller import fetch_and_save_cars
from sqlalchemy.future import select
from ..models.car import Car

router = APIRouter()

@router.post("/cars/fetch")
async def fetch_cars(
    start_lat: float, start_lon: float, end_lat: float, end_lon: float,
    date_time: str, passengers: list = [{"type": "ADULT"}],
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch cars using Amadeus API and save to the database.
    """
    try:
        start_location = {"latitude": start_lat, "longitude": start_lon}
        end_location = {"latitude": end_lat, "longitude": end_lon}
        await fetch_and_save_cars(db, start_location, end_location, date_time, passengers)
        return {"message": "Cars fetched and saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cars")
async def get_cars(page: int = 1, limit: int = 15, db: AsyncSession = Depends(get_db)):
    """
    Fetch cars from the database for the frontend.
    """
    cars = await db.execute(select(Car).offset((page - 1) * limit).limit(limit))
    return cars.scalars().all()
