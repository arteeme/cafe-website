import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()  # загружаем переменные из .env файла

# Используем SQLite вместо MySQL для простоты запуска
# Путь к файлу базы данных
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cafe.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

logger.info(f"Using database file at: {DB_PATH}")

# Закомментированные параметры MySQL для будущего использования
# DB_HOST = os.getenv('DB_HOST', 'localhost')
# DB_NAME = os.getenv('DB_NAME', 'cafedb')
# DB_USER = os.getenv('DB_USER', 'root')
# DB_PASSWORD = os.getenv('DB_PASSWORD', '')
# DB_DIALECT = os.getenv('DB_DIALECT', 'mysql')
# DATABASE_URL = f"{DB_DIALECT}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Создаем движок базы данных
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

# Создаем класс сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для моделей
Base = declarative_base()

# Функция для получения соединения с базой данных
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close() 