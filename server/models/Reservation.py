from sqlalchemy import Column, Integer, String, Date, Time, DateTime, Enum, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from db import Base

class Reservation(Base):
    __tablename__ = 'reservations'
    
    id = Column(Integer, primary_key=True)
    reservation_date = Column(Date, nullable=False)
    reservation_time = Column(Time, nullable=False)
    duration = Column(Integer, default=120)  # продолжительность в минутах, по умолчанию 2 часа
    guests_count = Column(Integer, nullable=False)
    status = Column(String(20), default='ожидание')
    special_requests = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Отношения
    user_id = Column(Integer, ForeignKey('users.id'))
    table_id = Column(Integer, ForeignKey('tables.id'))
    user = relationship("User", back_populates="reservations")
    table = relationship("Table", back_populates="reservations")
    
    def __init__(self, user_id, table_id, reservation_date, reservation_time, guests_count, 
                 duration=120, special_requests=None):
        self.user_id = user_id
        self.table_id = table_id
        self.reservation_date = reservation_date
        self.reservation_time = reservation_time
        self.guests_count = guests_count
        self.duration = duration
        self.special_requests = special_requests
    
    def to_dict(self):
        """Преобразует бронирование в словарь для API"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'table_id': self.table_id,
            'table_number': self.table.table_number if self.table else None,
            'reservation_date': self.reservation_date.isoformat() if self.reservation_date else None,
            'reservation_time': self.reservation_time.isoformat() if self.reservation_time else None,
            'duration': self.duration,
            'guests_count': self.guests_count,
            'status': self.status,
            'special_requests': self.special_requests,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_name': self.user.name if self.user else None
        }
    
    def __repr__(self):
        return f"<Reservation(id={self.id}, date='{self.reservation_date}', time='{self.reservation_time}', status='{self.status}')>" 