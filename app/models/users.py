from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    preferences = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    tickets = relationship("Ticket", back_populates="user", cascade="all, delete")

    messages = relationship("Message", back_populates="user", cascade="all, delete")