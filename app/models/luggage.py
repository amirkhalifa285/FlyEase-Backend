# app/models/luggage.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..base import Base

class Luggage(Base):
    __tablename__ = "luggage"

    # We treat this as the PRIMARY KEY (and the user sees it as their "baggage ID")
    luggage_id = Column(Integer, primary_key=True, autoincrement=True)

    weight = Column(Float, nullable=True)
    status = Column(String, nullable=True)
    last_location = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship back to Ticket
    ticket = relationship("Ticket", back_populates="luggage")
