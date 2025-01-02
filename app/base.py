from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


from .models.flight import Flight
from .models.location import Location
from .models.path import Path