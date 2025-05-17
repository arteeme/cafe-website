import os
from dotenv import load_dotenv

load_dotenv()  # Загрузка переменных из .env файла

# Базовая конфигурация для всех окружений
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'секретный_ключ_для_приложения')
    UPLOAD_FOLDER = os.getenv('UPLOAD_PATH', './static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB макс. размер файла
    JWT_SECRET_KEY = os.getenv('JWT_SECRET', 'секретный_ключ_для_jwt_токенов')
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24 * 30  # 30 дней

# Конфигурация для разработки
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///cafe.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True

# Конфигурация для тестирования
class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///test.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False

# Конфигурация для продакшна
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 1800
    }

# Словарь конфигураций
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

# Получение текущей конфигурации
def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    return config_by_name[env] 