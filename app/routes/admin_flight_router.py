from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.controllers.admin_flight_controller import (
    get_all_flights_admin,
    create_flight_admin,
    update_flight_admin,
)
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

class FlightCreateRequest(BaseModel):
    airline_name: str
    flight_number: str
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    status: str

class FlightUpdateRequest(BaseModel):
    airline_name: Optional[str] = None
    flight_number: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    status: Optional[str] = None

@router.get("/admin/flights")
async def admin_get_flights(db: AsyncSession = Depends(get_db)):
    return await get_all_flights_admin(db)

@router.post("/admin/flights")
async def admin_create_flight(flight_data: FlightCreateRequest, db: AsyncSession = Depends(get_db)):
    return await create_flight_admin(db, flight_data.dict())

@router.put("/admin/flights/{flight_number}")
async def admin_update_flight(flight_number: str, flight_data: FlightUpdateRequest, db: AsyncSession = Depends(get_db)):
    return await update_flight_admin(db, flight_number, flight_data.dict(exclude_unset=True))

# @router.delete("/admin/flights/{flight_number}")
# async def admin_delete_flight(flight_number: str, db: AsyncSession = Depends(get_db)):
#     return await delete_flight_admin(db, flight_number)
