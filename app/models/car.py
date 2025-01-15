from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from ..base import Base

class Car(Base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(String, nullable=False, unique=True)  # Unique ID for the transfer offer
    name = Column(String, nullable=False)  # Name of the vehicle or service
    vehicle_type = Column(String, nullable=True)  # Type of vehicle (e.g., sedan, van)
    model = Column(String, nullable=True)  # Model of the car, if provided
    location = Column(String, nullable=False)  # Pickup location
    price = Column(Float, nullable=True)  # Total price for the transfer
    currency = Column(String, nullable=True)  # Currency of the price
    fuel_type = Column(String, nullable=True)  # Type of fuel, if provided
    start_location = Column(JSON, nullable=True)  # JSON for pickup location coordinates
    end_location = Column(JSON, nullable=True)  # JSON for drop-off location coordinates
    start_time = Column(DateTime, nullable=True)  # Pickup date and time
    end_time = Column(DateTime, nullable=True)  # Drop-off date and time
    providers = Column(JSON, nullable=True)  # Provider details as JSON
    passengers = Column(JSON, nullable=True)  # Passenger details as JSON
    created_at = Column(DateTime, nullable=True)  # Record creation timestamp
