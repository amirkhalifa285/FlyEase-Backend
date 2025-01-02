from sqlalchemy import Column, Integer, String, JSON, Text
from ..base import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    category = Column(String, nullable=True)  # Optional category for grouping
    description = Column(Text, nullable=True)  # Optional description
    coordinates = Column(JSON, nullable=False)  # Required JSON field for coordinates
    #details = Column(JSON, nullable=True)  # Additional data (e.g., menu, hours)
