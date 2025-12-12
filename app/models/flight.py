# app/models/flight.py
from sqlalchemy import Column, Integer, String, DateTime, Index
from ..base import Base

class Flight(Base):
    __tablename__ = "flights"
    
    # Add composite index for common queries
    __table_args__ = (
        Index('ix_flights_origin_destination', 'origin', 'destination'),
        Index('ix_flights_departure', 'departure_time'),
    )

    id = Column(Integer, primary_key=True, index=True)
    airline_name = Column(String, nullable=False)
    flight_number = Column(String, nullable=False, unique=True, index=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)

    def to_dict(self):
        """
        Convert the Flight object to a dictionary.
        """
        return {
            "id": self.id,
            "airline_name": self.airline_name,
            "flight_number": self.flight_number,
            "origin": self.origin,
            "destination": self.destination,
            "departure_time": self.departure_time.isoformat() if self.departure_time else None,
            "arrival_time": self.arrival_time.isoformat() if self.arrival_time else None,
            "status": self.status,
        }