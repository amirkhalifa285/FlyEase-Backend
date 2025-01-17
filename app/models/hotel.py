from app.base import Base
from sqlalchemy import Column, String, Integer, Float, Text, Boolean

class Hotel(Base):
    __tablename__ = 'hotels'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    rating = Column(Float)
    total_ratings = Column(Integer)
    place_id = Column(String(255), unique=True, nullable=False)
    photo_reference = Column(Text)
    open_now = Column(Boolean)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "rating": self.rating,
            "total_ratings": self.total_ratings,
            "place_id": self.place_id,
            "photo_reference": self.photo_reference,
            "open_now": self.open_now
        }
