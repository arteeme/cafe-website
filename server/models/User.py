from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, func, ForeignKey, Table
from sqlalchemy.orm import relationship
import bcrypt
import os
import datetime
import hashlib
from db import Base

# Таблица связи пользователь-избранные блюда
user_favorites = Table(
    'user_favorites', 
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('menu_item_id', Integer, ForeignKey('menu_items.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(20))
    role = Column(String(20), default='user')
    reset_password_token = Column(String(100))
    reset_password_expire = Column(DateTime)
    avatar = Column(String(255), default='default-avatar.jpg')
    street = Column(String(255))
    city = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Отношения
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")
    contacts = relationship("Contact", back_populates="user")
    favorite_items = relationship("MenuItem", secondary=user_favorites, back_populates="favorited_by")
    
    def __init__(self, name, email, password, phone=None, role='user', avatar='default-avatar.jpg', 
                street=None, city=None, postal_code=None, country=None):
        self.name = name
        self.email = email
        self.set_password(password)
        self.phone = phone
        self.role = role
        self.avatar = avatar
        self.street = street
        self.city = city
        self.postal_code = postal_code
        self.country = country
    
    def set_password(self, password):
        """Хеширует пароль пользователя"""
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Проверяет, соответствует ли пароль хешу"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
    def get_reset_password_token(self):
        """Создает токен для сброса пароля"""
        # Генерируем случайный токен
        token_bytes = os.urandom(20)
        reset_token = hashlib.sha256(token_bytes).hexdigest()
        
        # Сохраняем хеш токена и время действия
        self.reset_password_token = reset_token
        self.reset_password_expire = datetime.datetime.now() + datetime.timedelta(minutes=10)
        
        return reset_token
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}', role='{self.role}')>" 