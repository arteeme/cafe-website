from models import User
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import func
from db import SessionLocal
from flask_jwt_extended import create_access_token, get_jwt_identity
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Вспомогательная функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# @desc    Регистрация нового пользователя
# @route   POST /api/auth/register
# @access  Public
def register_user(user_data):
    db = get_db()
    try:
        logger.debug(f"Начало регистрации пользователя. Данные: {user_data}")
        
        # Проверка наличия необходимых полей
        if not user_data or not all(key in user_data for key in ['name', 'email', 'password']):
            missing_fields = [field for field in ['name', 'email', 'password'] if field not in user_data]
            logger.error(f"Отсутствуют обязательные поля: {missing_fields}")
            return {
                'success': False,
                'message': 'Не все обязательные поля заполнены',
                'missing_fields': missing_fields
            }, 400
        
        # Проверка, что email уникален
        existing_user = db.query(User).filter(User.email == user_data.get('email').lower()).first()
        if existing_user:
            logger.warning(f"Пользователь с email {user_data.get('email')} уже существует")
            return {
                'success': False,
                'message': 'Пользователь с таким email уже существует'
            }, 400
        
        # Проверка сложности пароля
        if len(user_data.get('password', '')) < 6:
            logger.warning("Слишком короткий пароль")
            return {
                'success': False,
                'message': 'Пароль должен содержать минимум 6 символов'
            }, 400
        
        logger.info(f"Создание нового пользователя с email: {user_data.get('email')}")
        
        # Создание нового пользователя
        user = User(
            name=user_data.get('name'),
            email=user_data.get('email').lower(),
            password=user_data.get('password'),
            phone=user_data.get('phone'),
            role='user'  # по умолчанию обычный пользователь
        )
        
        # Добавление адреса, если есть
        if 'street' in user_data:
            user.street = user_data.get('street')
        if 'city' in user_data:
            user.city = user_data.get('city')
        if 'postal_code' in user_data:
            user.postal_code = user_data.get('postal_code')
        if 'country' in user_data:
            user.country = user_data.get('country')
        
        logger.debug("Добавление пользователя в базу данных...")
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Пользователь успешно создан с ID: {user.id}")
        
        # Создаем JWT токен
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'name': user.name,
                'email': user.email,
                'role': user.role
            }
        )
        
        logger.info(f"Пользователь зарегистрирован успешно: {user.email}, ID: {user.id}")
        
        return {
            'success': True,
            'message': 'Пользователь успешно зарегистрирован',
            'token': access_token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role
            }
        }, 201
    
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError при регистрации: {str(e)}")
        return {
            'success': False,
            'message': 'Ошибка регистрации: такой пользователь уже существует',
            'error': str(e)
        }, 400
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"SQLAlchemyError при регистрации: {str(e)}")
        return {
            'success': False,
            'message': 'Ошибка при регистрации пользователя',
            'error': str(e)
        }, 500
    except Exception as e:
        db.rollback()
        logger.error(f"Непредвиденная ошибка при регистрации: {str(e)}")
        import traceback
        logger.error(f"Трассировка: {traceback.format_exc()}")
        return {
            'success': False,
            'message': 'Непредвиденная ошибка при регистрации',
            'error': str(e)
        }, 500

# @desc    Вход пользователя
# @route   POST /api/auth/login
# @access  Public
def login_user(login_data):
    db = get_db()
    try:
        logger.debug(f"Login attempt with data: {login_data}")
        
        # Проверка наличия необходимых полей
        if not login_data or not all(key in login_data for key in ['email', 'password']):
            logger.error("Missing required fields in login data")
            return {
                'success': False,
                'message': 'Не все обязательные поля заполнены'
            }, 400
        
        email = login_data.get('email', '').lower()
        password = login_data.get('password', '')
        
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            logger.warning(f"Login attempt for non-existent user: {email}")
            return {
                'success': False,
                'message': 'Неверный email или пароль'
            }, 401
        
        if not user.check_password(password):
            logger.warning(f"Failed login attempt (wrong password) for user: {email}")
            return {
                'success': False,
                'message': 'Неверный email или пароль'
            }, 401
        
        # Создаем JWT токен
        access_token = create_access_token(
            identity=user.id, 
            additional_claims={
                'name': user.name,
                'email': user.email,
                'role': user.role
            }
        )
        
        logger.info(f"User logged in successfully: {user.email}, ID: {user.id}")
        
        return {
            'success': True,
            'token': access_token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role
            }
        }
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"SQLAlchemyError during login: {str(e)}")
        return {
            'success': False,
            'message': 'Ошибка при входе в систему',
            'error': str(e)
        }, 500
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during login: {str(e)}")
        return {
            'success': False,
            'message': 'Непредвиденная ошибка при входе',
            'error': str(e)
        }, 500

# @desc    Получение информации о текущем пользователе
# @route   GET /api/auth/me
# @access  Private
def get_current_user():
    user_id = get_jwt_identity()
    db = get_db()
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return {
                'success': False,
                'message': 'Пользователь не найден'
            }, 404
        
        return {
            'success': True,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'role': user.role,
                'avatar': user.avatar,
                'street': user.street,
                'city': user.city,
                'postal_code': user.postal_code,
                'country': user.country,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        }
    
    except SQLAlchemyError as e:
        return {
            'success': False,
            'message': 'Ошибка при получении данных пользователя',
            'error': str(e)
        }, 500

# @desc    Обновление данных пользователя
# @route   PUT /api/auth/me
# @access  Private
def update_user(user_data):
    user_id = get_jwt_identity()
    db = get_db()
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return {
                'success': False,
                'message': 'Пользователь не найден'
            }, 404
        
        # Обновляем поля пользователя
        if 'name' in user_data:
            user.name = user_data['name']
        if 'phone' in user_data:
            user.phone = user_data['phone']
        if 'avatar' in user_data:
            user.avatar = user_data['avatar']
        
        # Обновляем адрес
        if 'street' in user_data:
            user.street = user_data['street']
        if 'city' in user_data:
            user.city = user_data['city']
        if 'postal_code' in user_data:
            user.postal_code = user_data['postal_code']
        if 'country' in user_data:
            user.country = user_data['country']
        
        # Обновляем пароль, если он был передан
        if 'password' in user_data and user_data['password']:
            user.set_password(user_data['password'])
        
        db.commit()
        
        return {
            'success': True,
            'message': 'Данные пользователя обновлены',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'role': user.role,
                'avatar': user.avatar
            }
        }
    
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при обновлении данных пользователя',
            'error': str(e)
        }, 500

# @desc    Запрос сброса пароля
# @route   POST /api/auth/forgot-password
# @access  Public
def forgot_password(email_data):
    email = email_data.get('email', '').lower()
    
    if not email:
        return {
            'success': False,
            'message': 'Email обязателен'
        }, 400
    
    db = get_db()
    
    try:
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return {
                'success': False,
                'message': 'Пользователь с таким email не найден'
            }, 404
        
        # Генерируем токен сброса пароля
        reset_token = user.get_reset_password_token()
        db.commit()
        
        # Здесь можно добавить отправку email с токеном для сброса пароля
        # В реальном приложении, но для демонстрации просто возвращаем 
        # сообщение об успехе
        
        return {
            'success': True,
            'message': 'Инструкции по сбросу пароля отправлены на указанный email',
            'reset_token': reset_token  # В реальном приложении токен не возвращается
        }
    
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при запросе сброса пароля',
            'error': str(e)
        }, 500

# @desc    Сброс пароля
# @route   POST /api/auth/reset-password
# @access  Public
def reset_password(reset_data):
    # Реализация сброса пароля
    # В реальном приложении здесь была бы проверка токена и сброс пароля
    return {
        'success': True,
        'message': 'Пароль успешно сброшен'
    }

# @desc    Получение списка избранных блюд пользователя
# @route   GET /api/favorites
# @access  Private
def get_favorites():
    user_id = get_jwt_identity()
    db = get_db()
    
    try:
        # В реальном приложении здесь был бы запрос к таблице избранных блюд
        # Пример заглушки
        return {
            'success': True,
            'favorites': [
                {
                    'id': 1,
                    'name': 'Бургер "Классический"',
                    'price': 300,
                    'description': 'Сочная говяжья котлета с сыром, салатом и соусом',
                    'image': '/images/burger.jpg'
                },
                {
                    'id': 2,
                    'name': 'Пицца "Маргарита"',
                    'price': 400,
                    'description': 'Традиционная итальянская пицца с томатами и моцареллой',
                    'image': '/images/pizza.jpg'
                }
            ]
        }
    except SQLAlchemyError as e:
        return {
            'success': False,
            'message': 'Ошибка при получении избранных блюд',
            'error': str(e)
        }, 500

# @desc    Добавление блюда в избранное
# @route   POST /api/favorites/:id
# @access  Private
def add_favorite(item_id):
    user_id = get_jwt_identity()
    db = get_db()
    
    try:
        # В реальном приложении здесь было бы добавление записи в таблицу избранных блюд
        return {
            'success': True,
            'message': 'Блюдо добавлено в избранное'
        }
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при добавлении блюда в избранное',
            'error': str(e)
        }, 500

# @desc    Удаление блюда из избранного
# @route   DELETE /api/favorites/:id
# @access  Private
def remove_favorite(item_id):
    user_id = get_jwt_identity()
    db = get_db()
    
    try:
        # В реальном приложении здесь было бы удаление записи из таблицы избранных блюд
        return {
            'success': True,
            'message': 'Блюдо удалено из избранного'
        }
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при удалении блюда из избранного',
            'error': str(e)
        }, 500

# @desc    Получение списка адресов доставки пользователя
# @route   GET /api/addresses
# @access  Private
def get_addresses():
    user_id = get_jwt_identity()
    db = get_db()
    
    try:
        # В реальном приложении здесь был бы запрос к таблице адресов
        # Пример заглушки
        return {
            'success': True,
            'addresses': [
                {
                    'id': 1,
                    'title': 'Дом',
                    'street': 'ул. Примерная, д. 123',
                    'city': 'Москва',
                    'postal': '123456',
                    'notes': 'Подъезд 1, этаж 5, кв. 789'
                },
                {
                    'id': 2,
                    'title': 'Работа',
                    'street': 'ул. Деловая, д. 45',
                    'city': 'Москва',
                    'postal': '654321',
                    'notes': 'Бизнес-центр "Успех", офис 301'
                }
            ]
        }
    except SQLAlchemyError as e:
        return {
            'success': False,
            'message': 'Ошибка при получении адресов доставки',
            'error': str(e)
        }, 500

# @desc    Добавление адреса доставки
# @route   POST /api/addresses
# @access  Private
def add_address(address_data):
    user_id = get_jwt_identity()
    db = get_db()
    
    try:
        # В реальном приложении здесь было бы добавление записи в таблицу адресов
        return {
            'success': True,
            'message': 'Адрес добавлен',
            'address': {
                'id': 3,  # В реальном приложении был бы ID из базы
                'title': address_data.get('title'),
                'street': address_data.get('street'),
                'city': address_data.get('city'),
                'postal': address_data.get('postal'),
                'notes': address_data.get('notes')
            }
        }
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при добавлении адреса',
            'error': str(e)
        }, 500

# @desc    Обновление адреса доставки
# @route   PUT /api/addresses/:id
# @access  Private
def update_address(address_id, address_data):
    user_id = get_jwt_identity()
    db = get_db()
    
    try:
        # В реальном приложении здесь было бы обновление записи в таблице адресов
        return {
            'success': True,
            'message': 'Адрес обновлен',
            'address': {
                'id': address_id,
                'title': address_data.get('title'),
                'street': address_data.get('street'),
                'city': address_data.get('city'),
                'postal': address_data.get('postal'),
                'notes': address_data.get('notes')
            }
        }
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при обновлении адреса',
            'error': str(e)
        }, 500

# @desc    Удаление адреса доставки
# @route   DELETE /api/addresses/:id
# @access  Private
def delete_address(address_id):
    user_id = get_jwt_identity()
    db = get_db()
    
    try:
        # В реальном приложении здесь было бы удаление записи из таблицы адресов
        return {
            'success': True,
            'message': 'Адрес удален'
        }
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при удалении адреса',
            'error': str(e)
        }, 500 