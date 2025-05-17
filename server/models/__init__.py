from db import Base, engine

# Импортируем все модели для регистрации их в метаданных
from models.User import User
from models.MenuItem import MenuItem
from models.Table import Table
from models.Reservation import Reservation
from models.Review import Review
from models.Contact import Contact
from models.Order import Order, OrderItem
from models.Category import Category

# Экспортируем все модели для удобства импорта
__all__ = [
    'User',
    'MenuItem',
    'Table',
    'Reservation',
    'Review',
    'Contact',
    'Order',
    'OrderItem',
    'Category'
]

# Функция для создания всех таблиц в базе данных
def create_tables():
    Base.metadata.create_all(engine)

# Функция для удаления всех таблиц из базы данных
def drop_tables():
    Base.metadata.drop_all(engine) 