from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..base import Base

class Luggage(Base):
    __tablename__ = "luggage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    luggage_id = Column(Integer, ForeignKey("tickets.luggage_id"), unique=True, nullable=False)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    weight = Column(Float, nullable=True)
    status = Column(String, nullable=True)
    last_location = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship with Ticket
    ticket = relationship(
        "Ticket",
        back_populates="luggage",
        foreign_keys="[Luggage.ticket_id]",  # Specify the foreign key
    )