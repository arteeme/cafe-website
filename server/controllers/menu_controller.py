from models import MenuItem, Review
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, or_
from db import SessionLocal

# Вспомогательная функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# @desc    Получить все пункты меню
# @route   GET /api/menu
# @access  Public
def get_menu_items():
    db = get_db()
    try:
        menu_items = db.query(MenuItem).order_by(MenuItem.name).all()
        return {
            'success': True,
            'count': len(menu_items),
            'data': [item.to_dict() for item in menu_items]
        }
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при получении пунктов меню',
            'error': str(e)
        }, 500

# @desc    Получить пункт меню по ID
# @route   GET /api/menu/:id
# @access  Public
def get_menu_item(item_id):
    db = get_db()
    try:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        
        if not menu_item:
            return {
                'success': False,
                'message': 'Пункт меню не найден'
            }, 404
        
        # Получение отзывов для блюда
        reviews = db.query(Review).filter(
            Review.menu_item_id == item_id,
            Review.approved == 1  # Только одобренные отзывы
        ).all()
        
        item_data = menu_item.to_dict()
        item_data['reviews'] = [review.to_dict() for review in reviews]
        
        return {
            'success': True,
            'data': item_data
        }
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при получении пункта меню',
            'error': str(e)
        }, 500

# @desc    Создать новый пункт меню
# @route   POST /api/menu
# @access  Private (Admin)
def create_menu_item(item_data):
    db = get_db()
    try:
        menu_item = MenuItem(
            name=item_data.get('name'),
            description=item_data.get('description'),
            price=item_data.get('price'),
            category=item_data.get('category'),
            image=item_data.get('image', 'default-food.jpg'),
            is_popular=item_data.get('is_popular', False),
            is_special_offer=item_data.get('is_special_offer', False)
        )
        
        db.add(menu_item)
        db.commit()
        db.refresh(menu_item)
        
        return {
            'success': True,
            'data': menu_item.to_dict()
        }, 201
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при создании пункта меню',
            'error': str(e)
        }, 500

# @desc    Обновить пункт меню
# @route   PUT /api/menu/:id
# @access  Private (Admin)
def update_menu_item(item_id, item_data):
    db = get_db()
    try:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        
        if not menu_item:
            return {
                'success': False,
                'message': 'Пункт меню не найден'
            }, 404
        
        # Обновляем поля, если они присутствуют в запросе
        if 'name' in item_data:
            menu_item.name = item_data['name']
        if 'description' in item_data:
            menu_item.description = item_data['description']
        if 'price' in item_data:
            menu_item.price = item_data['price']
        if 'image' in item_data:
            menu_item.image = item_data['image']
        if 'category' in item_data:
            menu_item.category = item_data['category']
        if 'is_popular' in item_data:
            menu_item.is_popular = item_data['is_popular']
        if 'is_special_offer' in item_data:
            menu_item.is_special_offer = item_data['is_special_offer']
        
        db.commit()
        db.refresh(menu_item)
        
        return {
            'success': True,
            'data': menu_item.to_dict()
        }
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при обновлении пункта меню',
            'error': str(e)
        }, 500

# @desc    Удалить пункт меню
# @route   DELETE /api/menu/:id
# @access  Private (Admin)
def delete_menu_item(item_id):
    db = get_db()
    try:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        
        if not menu_item:
            return {
                'success': False,
                'message': 'Пункт меню не найден'
            }, 404
        
        db.delete(menu_item)
        db.commit()
        
        return {
            'success': True,
            'message': 'Пункт меню успешно удален'
        }
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при удалении пункта меню',
            'error': str(e)
        }, 500

# @desc    Получить популярные блюда
# @route   GET /api/menu/popular
# @access  Public
def get_popular_items():
    db = get_db()
    try:
        popular_items = db.query(MenuItem).filter(MenuItem.is_popular == True).limit(6).all()
        
        return {
            'success': True,
            'data': [item.to_dict() for item in popular_items]
        }
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при получении популярных блюд',
            'error': str(e)
        }, 500

# @desc    Получить блюда по категории
# @route   GET /api/menu/category/:category
# @access  Public
def get_items_by_category(category):
    db = get_db()
    try:
        items = db.query(MenuItem).filter(MenuItem.category == category).order_by(MenuItem.name).all()
        
        return {
            'success': True,
            'count': len(items),
            'data': [item.to_dict() for item in items]
        }
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при получении блюд по категории',
            'error': str(e)
        }, 500

# @desc    Поиск блюд по названию или описанию
# @route   GET /api/menu/search?q=
# @access  Public
def search_menu_items(query):
    if not query:
        return {
            'success': False,
            'message': 'Укажите поисковый запрос'
        }, 400
    
    db = get_db()
    try:
        search_pattern = f"%{query}%"
        items = db.query(MenuItem).filter(
            or_(
                MenuItem.name.ilike(search_pattern),
                MenuItem.description.ilike(search_pattern)
            )
        ).order_by(MenuItem.name).all()
        
        return {
            'success': True,
            'count': len(items),
            'data': [item.to_dict() for item in items]
        }
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при поиске блюд',
            'error': str(e)
        }, 500 