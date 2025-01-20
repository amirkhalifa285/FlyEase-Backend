from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..base import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    airline_name = Column(String, nullable=False)
    flight_number = Column(String, nullable=False)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="tickets")

    luggage_id = Column(Integer, ForeignKey("luggage.luggage_id"), unique=True, nullable=True)

    luggage = relationship("Luggage", back_populates="ticket", uselist=False)

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
            "luggage_id": self.luggage_id,
        }