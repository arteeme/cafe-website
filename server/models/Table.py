from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, func
from sqlalchemy.orm import relationship
from db import Base

class Table(Base):
    __tablename__ = 'tables'
    
    id = Column(Integer, primary_key=True)
    table_number = Column(Integer, nullable=False, unique=True)
    capacity = Column(Integer, nullable=False)
    location = Column(String(20), default='в центре')
    is_available = Column(Boolean, default=True)
    description = Column(String(255))
    image = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Отношения
    reservations = relationship("Reservation", back_populates="table")
    
    def __init__(self, table_number, capacity, location='в центре', is_available=True, description=None, image=None):
        self.table_number = table_number
        self.capacity = capacity
        self.location = location
        self.is_available = is_available
        self.description = description
        self.image = image
    
    def to_dict(self):
        """Преобразует столик в словарь для API"""
        return {
            'id': self.id,
            'table_number': self.table_number,
            'capacity': self.capacity,
            'location': self.location,
            'is_available': self.is_available,
            'description': self.description,
            'image': self.image
        }
    
    def __repr__(self):
        return f"<Table(id={self.id}, number={self.table_number}, capacity={self.capacity}, location='{self.location}')>" 