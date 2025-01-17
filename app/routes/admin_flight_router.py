from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.controllers.admin_flight_controller import (
    get_all_flights_admin,
    create_flight_admin,
    update_flight_admin,
    delete_flight_admin
)
from pydantic import BaseModel

router = APIRouter()

class FlightCreateRequest(BaseModel):
    airline_name: str
    flight_number: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    status: str

class FlightUpdateRequest(BaseModel):
    airline_name: str = None
    flight_number: str = None
    origin: str = None
    destination: str = None
    departure_time: str = None
    arrival_time: str = None
    status: str = None

@router.get("/admin/flights")
async def admin_get_flights(db: AsyncSession = Depends(get_db)):
    return await get_all_flights_admin(db)

@router.post("/admin/flights")
async def admin_create_flight(flight_data: FlightCreateRequest, db: AsyncSession = Depends(get_db)):
    return await create_flight_admin(db, flight_data.dict())

@router.put("/admin/flights/{flight_id}")
async def admin_update_flight(flight_id: int, flight_data: FlightUpdateRequest, db: AsyncSession = Depends(get_db)):
    return await update_flight_admin(db, flight_id, flight_data.dict(exclude_unset=True))

@router.delete("/admin/flights/{flight_id}")
async def admin_delete_flight(flight_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_flight_admin(db, flight_id)