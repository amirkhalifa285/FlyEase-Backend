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