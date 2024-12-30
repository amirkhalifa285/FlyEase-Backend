from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.database import get_db
from ..controllers.flight_controller import get_all_flights, create_flight  # Adjust if necessary
from pydantic import BaseModel

# Define the router
router = APIRouter()

# Pydantic schema for input validation
class FlightCreate(BaseModel):
    status: str
    gate: str

@router.get("/flights")
async def fetch_flights(db: AsyncSession = Depends(get_db)):
    return await get_all_flights(db)

@router.post("/flights")
async def add_flight(flight_data: FlightCreate, db: AsyncSession = Depends(get_db)):
    return await create_flight(db, flight_data.dict())
