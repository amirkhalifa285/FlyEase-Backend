# app/models/flight.py
from sqlalchemy import Column, Integer, String, DateTime
from ..base import Base

class Flight(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, index=True)
    airline_name = Column(String, nullable=False)
    flight_number = Column(String, nullable=False)
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
