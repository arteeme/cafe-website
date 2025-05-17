from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, func, ForeignKey
from sqlalchemy.orm import relationship
import datetime
import random
from db import Base

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    order_number = Column(String(50), unique=True)
    status = Column(String(20), default='новый')
    order_type = Column(String(20), nullable=False)
    total_amount = Column(Float, nullable=False)
    payment_status = Column(String(20), default='ожидание')
    payment_method = Column(String(20), default='наличные')
    address = Column(String(255))
    phone = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    comment = Column(String(500))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime)
    
    # Отношения
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __init__(self, user_id, total_amount, order_type, payment_method, phone, name,
                address=None, comment=None):
        self.user_id = user_id
        self.total_amount = total_amount
        self.order_type = order_type
        self.payment_method = payment_method
        self.phone = phone
        self.name = name
        self.address = address
        self.comment = comment
        self.generate_order_number()
    
    def generate_order_number(self):
        """Генерирует уникальный номер заказа"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        random_part = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        self.order_number = f"ORD-{timestamp}-{random_part}"
    
    def to_dict(self):
        """Преобразует заказ в словарь для API"""
        return {
            'id': self.id,
            'order_number': self.order_number,
            'status': self.status,
            'order_type': self.order_type,
            'total_amount': self.total_amount,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'address': self.address,
            'phone': self.phone,
            'name': self.name,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'items': [item.to_dict() for item in self.items] if self.items else []
        }
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_number='{self.order_number}', status='{self.status}', total={self.total_amount})>"

class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    notes = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    
    # Отношения
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    menu_item_id = Column(Integer, ForeignKey('menu_items.id'), nullable=False)
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")
    
    def __init__(self, order_id, menu_item_id, quantity, price, notes=None):
        self.order_id = order_id
        self.menu_item_id = menu_item_id
        self.quantity = quantity
        self.price = price
        self.subtotal = price * quantity
        self.notes = notes
    
    def to_dict(self):
        """Преобразует элемент заказа в словарь для API"""
        return {
            'id': self.id,
            'menu_item_id': self.menu_item_id,
            'menu_item_name': self.menu_item.name if self.menu_item else None,
            'quantity': self.quantity,
            'price': self.price,
            'subtotal': self.subtotal,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, item_id={self.menu_item_id}, quantity={self.quantity}, subtotal={self.subtotal})>" 