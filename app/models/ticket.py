from sqlalchemy import Column, Integer, String, DateTime, Float
from ..base import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    airline_name = Column(String, nullable=False)
    flight_number = Column(String, nullable=False)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "airline_name": self.airline_name,
            "flight_number": self.flight_number,
            "origin": self.origin,
            "destination": self.destination,
            "departure_time": self.departure_time.isoformat(),
            "arrival_time": self.arrival_time.isoformat(),
            "price": self.price,
        }