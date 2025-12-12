
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models so they are registered with Base.metadata
# This is required for Alembic migrations to detect all tables
from .models.flight import Flight
from .models.location import Location
from .models.path import Path
from .models.ticket import Ticket
from .models.luggage import Luggage
from .models.users import User
from .models.messages import Message
from .models.hotel import Hotel
from .models.car import Car
from .models.wall import Wall
