# from sqlalchemy.ext.asyncio import AsyncSession
# from ..models.service import Service
# from sqlalchemy.future import select
# #from ..db.database import SessionLocal


# """ def get_all_services():
#     db = SessionLocal()
#     services = db.query(Service).all()
#     db.close()
#     return services """

# async def get_all_services(db: AsyncSession):
#     result = await db.execute(select(Service))
#     return result.scalars().all()

# async def create_service(db: AsyncSession, service_data: dict):
#     #db = SessionLocal()
#     new_service = Service(**service_data)
#     db.add(new_service)
#     await db.commit()
#     await db.refresh(new_service)
#     #db.close()
#     return new_service
