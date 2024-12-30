from sqlalchemy import Column, Integer, String, Float, JSON
from ..base import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # e.g., gate, security, lounge
    coordinates = Column(JSON, nullable=True)  # Optional: For map rendering
