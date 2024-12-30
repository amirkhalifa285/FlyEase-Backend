from sqlalchemy import Column, Integer, Float, ForeignKey
from ..base import Base

class Path(Base):
    __tablename__ = "paths"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    destination_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    distance = Column(Float, nullable=False)  # Distance or travel time
