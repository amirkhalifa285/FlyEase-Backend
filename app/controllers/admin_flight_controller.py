from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.models.flight import Flight
from datetime import datetime

async def get_all_flights_admin(db: AsyncSession):
    """
    Retrieve all flights from the database (Admin View).
    """
    try:
        result = await db.execute(select(Flight))
        flights = result.scalars().all()
        return [flight.to_dict() for flight in flights]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching flights: {str(e)}")
async def create_flight_admin(db: AsyncSession, flight_data: dict):
    try:
        # Parse datetime strings into datetime.datetime objects
        if isinstance(flight_data.get("departure_time"), str):
            flight_data["departure_time"] = datetime.fromisoformat(flight_data["departure_time"])
        if isinstance(flight_data.get("arrival_time"), str):
            flight_data["arrival_time"] = datetime.fromisoformat(flight_data["arrival_time"])

        new_flight = Flight(**flight_data)
        db.add(new_flight)
        await db.commit()
        await db.refresh(new_flight)
        return new_flight
    except Exception as e:
        print(f"Error saving flight: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving flight: {str(e)}")


async def update_flight_admin(db: AsyncSession, flight_id: int, updated_data: dict):
    """
    Update an existing flight's details (Admin Functionality).
    """
    try:
        # Fetch the flight record
        flight = await db.execute(select(Flight).where(Flight.id == flight_id))
        flight = flight.scalar_one_or_none()

        if not flight:
            raise HTTPException(status_code=404, detail="Flight not found")

        # Convert `departure_time` and `arrival_time` to datetime if provided as strings
        if "departure_time" in updated_data and isinstance(updated_data["departure_time"], str):
            updated_data["departure_time"] = datetime.fromisoformat(updated_data["departure_time"])
        if "arrival_time" in updated_data and isinstance(updated_data["arrival_time"], str):
            updated_data["arrival_time"] = datetime.fromisoformat(updated_data["arrival_time"])

        # Update the flight record
        for key, value in updated_data.items():
            setattr(flight, key, value)

        await db.commit()
        await db.refresh(flight)
        return flight.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating flight: {str(e)}")


async def delete_flight_admin(db: AsyncSession, flight_id: int):
    """
    Delete a flight from the database (Admin Functionality).
    """
    try:
        flight = await db.execute(select(Flight).where(Flight.id == flight_id))
        flight = flight.scalar_one_or_none()
        if not flight:
            raise HTTPException(status_code=404, detail="Flight not found")
        
        await db.delete(flight)
        await db.commit()
        return {"message": "Flight deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting flight: {str(e)}")