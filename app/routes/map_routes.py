from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.controllers.map_controller import populate_mock_map, get_map_data

router = APIRouter()

@router.post("/map/populate")
async def populate_map(db: AsyncSession = Depends(get_db)):
    await populate_mock_map(db)
    return {"message": "Mock map data populated successfully"}

@router.get("/map")
async def fetch_map(db: AsyncSession = Depends(get_db)):
    return await get_map_data(db)
