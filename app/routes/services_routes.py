# from fastapi import APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from ..db.database import get_db
# from ..controllers.service_controller import get_all_services, create_service
# from pydantic import BaseModel

# router = APIRouter()

# class ServiceCreate(BaseModel):
#     name: str
#     description: str

# @router.get("/services")
# async def fetch_services(db: AsyncSession = Depends(get_db)):
#     return await get_all_services(db)

# @router.post("/services")
# async def add_service(service_data: ServiceCreate, db: AsyncSession = Depends(get_db)):
#     return await create_service(db, service_data.dict())
