from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, func, ForeignKey, Table
from sqlalchemy.orm import relationship
from db import Base
from models.User import user_favorites

class MenuItem(Base):
    __tablename__ = 'menu_items'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    price = Column(Float, nullable=False)
    image = Column(String(255), default='default-food.jpg')
    category = Column(String(50), nullable=False)
    is_popular = Column(Boolean, default=False)
    is_special_offer = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Отношения
    reviews = relationship("Review", back_populates="menu_item")
    order_items = relationship("OrderItem", back_populates="menu_item")
    favorited_by = relationship("User", secondary=user_favorites, back_populates="favorite_items")
    category_rel = relationship("Category", back_populates="menu_items")
    
    def __init__(self, name, description, price, category, image='default-food.jpg', 
                is_popular=False, is_special_offer=False, is_available=True):
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.image = image
        self.is_popular = is_popular
        self.is_special_offer = is_special_offer
        self.is_available = is_available
    
    def to_dict(self):
        """Возвращает словарь с данными о блюде"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image': self.image,
            'category': self.category,
            'is_popular': self.is_popular,
            'is_special_offer': self.is_special_offer,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<MenuItem(id={self.id}, name='{self.name}', price={self.price}, category='{self.category}')>" 