from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.controllers.map_controller import (
    add_location,
    add_path,
    update_location,
    delete_location,
    get_map_data,
    populate_mock_map,
    calculate_shortest_path,
    update_and_fetch_congestion
)

from ..auth.auth_utils import admin_only
from pydantic import BaseModel

class NavigationRequest(BaseModel):
    source_id: int
    destination_id: int

router = APIRouter()

@router.post("/map/populate")
async def populate_map(db: AsyncSession = Depends(get_db)):
    await populate_mock_map(db)
    return {"message": "Mock map data populated successfully"}

@router.get("/map")
async def fetch_map(db: AsyncSession = Depends(get_db)):
    # Call the controller function to get map data
    return await get_map_data(db)

@router.post("/map/navigate")
async def navigate(request: NavigationRequest, db: AsyncSession = Depends(get_db)):
    # Extract source_id and destination_id from the request
    return await calculate_shortest_path(request.source_id, request.destination_id, db)

#admin
@router.post("/admin/map/location")
async def create_location(location_data: dict, db: AsyncSession = Depends(get_db)):
    return await add_location(location_data, db)

@router.post("/admin/map/path")
async def create_path(path_data: dict, db: AsyncSession = Depends(get_db)):
    return await add_path(path_data, db)

@router.put("/admin/map/location/{location_id}", dependencies=[Depends(admin_only)])
async def modify_location(
    location_id: int,
    location_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing location with the given location_id.
    Only admins can access this route.
    """
    return await update_location(location_id, location_data, db)

@router.delete("/admin/map/location/{location_id}", dependencies=[Depends(admin_only)])
async def remove_location(
    location_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an existing location with the given location_id.
    Only admins can access this route.
    """
    return await delete_location(location_id, db)


@router.post("/map/update-congestion")
async def update_and_fetch_congestion_route(db: AsyncSession = Depends(get_db)):
    return await update_and_fetch_congestion(db)
    