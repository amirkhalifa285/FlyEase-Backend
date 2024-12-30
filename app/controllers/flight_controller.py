from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.flight import Flight

async def get_all_flights(db: AsyncSession):
    result = await db.execute(select(Flight))
    return result.scalars().all()

async def create_flight(db: AsyncSession, flight_data: dict):
    new_flight = Flight(**flight_data)
    db.add(new_flight)
    await db.commit()
    await db.refresh(new_flight)
    return new_flight
