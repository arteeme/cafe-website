from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from db import Base

class Contact(Base):
    __tablename__ = 'contacts'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20))
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(Enum('новое', 'прочитано', 'отвечено', 'закрыто', name='contact_statuses'), default='новое')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Отношения (опционально - пользователь мог отправить сообщение, будучи авторизованным)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user = relationship("User", back_populates="contacts")
    
    def __init__(self, name, email, subject, message, phone=None, user_id=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.subject = subject
        self.message = message
        self.user_id = user_id
    
    def to_dict(self):
        """Преобразует контактное сообщение в словарь для API"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'subject': self.subject,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_id': self.user_id
        }
    
    def __repr__(self):
        return f"<Contact(id={self.id}, name='{self.name}', email='{self.email}', status='{self.status}')>" 