from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from db import Base

class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    rating = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    approved = Column(Integer, default=0)  # 0 - на проверке, 1 - одобрен, -1 - отклонен
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Отношения
    user_id = Column(Integer, ForeignKey('users.id'))
    menu_item_id = Column(Integer, ForeignKey('menu_items.id'))
    user = relationship("User", back_populates="reviews")
    menu_item = relationship("MenuItem", back_populates="reviews")
    
    def __init__(self, user_id, menu_item_id, rating, text, approved=0):
        self.user_id = user_id
        self.menu_item_id = menu_item_id
        self.rating = rating
        self.text = text
        self.approved = approved
    
    def to_dict(self):
        """Преобразует отзыв в словарь для API"""
        return {
            'id': self.id,
            'rating': self.rating,
            'text': self.text,
            'approved': self.approved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id,
            'menu_item_id': self.menu_item_id,
            'user_name': self.user.name if self.user else None,
            'menu_item_name': self.menu_item.name if self.menu_item else None
        }
    
    def __repr__(self):
        return f"<Review(id={self.id}, user_id={self.user_id}, menu_item_id={self.menu_item_id}, rating={self.rating})>" 