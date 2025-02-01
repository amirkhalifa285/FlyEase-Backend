from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from datetime import datetime
from app.models.ticket import Ticket 
from app.models.messages import Message
from app.websocket.notifications import broadcast_message

async def get_all_flights_admin(db: AsyncSession):
    """
    Retrieve all flights (Tickets) from the database (Admin View).
    """
    try:
        result = await db.execute(select(Ticket))
        flights = result.scalars().all()
        return [flight.to_dict() for flight in flights]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching flights: {str(e)}")
    

async def create_flight_admin(db: AsyncSession, flight_data: dict):
    try:
        # Parse datetime strings into datetime objects
        if isinstance(flight_data.get("departure_time"), str):
            flight_data["departure_time"] = datetime.fromisoformat(flight_data["departure_time"])
        if isinstance(flight_data.get("arrival_time"), str):
            flight_data["arrival_time"] = datetime.fromisoformat(flight_data["arrival_time"])

        new_flight = Ticket(**flight_data)
        db.add(new_flight)
        await db.commit()
        await db.refresh(new_flight)
        return new_flight.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving flight: {str(e)}")


async def update_flight_admin(db: AsyncSession, flight_number: str, updated_data: dict):
    """
    Update an existing flight's details using flight_number (Admin Functionality).
    """
    try:
        result = await db.execute(select(Ticket).where(Ticket.flight_number == flight_number))
        flight = result.scalar_one_or_none()

        if not flight:
            raise HTTPException(status_code=404, detail="Flight not found")

        # Convert datetime strings to datetime objects
        if "departure_time" in updated_data and isinstance(updated_data["departure_time"], str):
            updated_data["departure_time"] = datetime.fromisoformat(updated_data["departure_time"])
        if "arrival_time" in updated_data and isinstance(updated_data["arrival_time"], str):
            updated_data["arrival_time"] = datetime.fromisoformat(updated_data["arrival_time"])

        # Update fields
        for key, value in updated_data.items():
            setattr(flight, key, value)

        await db.commit()
        await db.refresh(flight)

        # Notify users and save to database
        message_content = f"Flight {flight_number} status changed to: {updated_data.get('status', 'updated')}"
        await notify_users_about_flight(flight_number, message_content, db)

        # Broadcast WebSocket message
        await broadcast_message(message_content)

        return flight.to_dict()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating flight: {str(e)}")


async def notify_users_about_flight(flight_number: str, content: str, db: AsyncSession):
    """Create messages for users who booked this flight"""
    # Get all users with tickets for this flight
    result = await db.execute(
        select(Ticket.user_id).where(Ticket.flight_number == flight_number)
    )
    user_ids = result.scalars().all()

    # Create a message for each user
    for user_id in user_ids:
        new_message = Message(
            user_id=user_id,
            content=content,
            status="unread"
        )
        db.add(new_message)
    
    await db.commit()  # Commit the messages


async def delete_flight_admin(db: AsyncSession, flight_number: str):
    """
    Delete a flight from the database (Admin Functionality).
    """
    try:
        result = await db.execute(select(Ticket).where(Ticket.flight_number == flight_number))
        flight = result.scalar_one_or_none()
        if not flight:
            raise HTTPException(status_code=404, detail="Flight not found")
        
        await db.delete(flight)
        await db.commit()
        return {"message": "Flight deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting flight: {str(e)}")