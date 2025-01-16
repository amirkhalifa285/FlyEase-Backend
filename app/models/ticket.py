from sqlalchemy import Column, Integer, String, DateTime, Float
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
    luggage_id = Column(Integer, unique=True, nullable=True, index=True)

    luggage = relationship(
        "Luggage",
        back_populates="ticket",
        foreign_keys="[Luggage.ticket_id]",  # Explicitly set the foreign key for this relationship
        uselist=False,
    )

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
