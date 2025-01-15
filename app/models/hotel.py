from sqlalchemy import Column, Integer, String, Float, DateTime
from ..base import Base

class Hotel(Base):
    __tablename__ = "hotels"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(String, unique=True, nullable=False)  # Unique ID for the hotel
    name = Column(String, nullable=False)  # Hotel name
    chain_code = Column(String, nullable=True)  # Chain code
    iata_code = Column(String, nullable=True)  # IATA location code
    location = Column(String, nullable=False)  # Location of the hotel
    latitude = Column(Float, nullable=True)  # Latitude
    longitude = Column(Float, nullable=True)  # Longitude
    last_update = Column(DateTime, nullable=True)  # Last update timestamp
