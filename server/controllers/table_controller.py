from models import Table
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import SessionLocal
from flask_jwt_extended import get_jwt_identity

# Вспомогательная функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# @desc    Добавление нового столика
# @route   POST /api/tables
# @access  Private/Admin
def create_table(table_data):
    db = get_db()
    try:
        # Проверка уникальности номера столика
        existing_table = db.query(Table).filter(Table.table_number == table_data.get('table_number')).first()
        if existing_table:
            return {
                'success': False,
                'message': 'Столик с таким номером уже существует'
            }, 400
        
        # Создание нового столика
        table = Table(
            table_number=table_data.get('table_number'),
            capacity=table_data.get('capacity'),
            location=table_data.get('location', 'в центре'),
            is_available=table_data.get('is_available', True),
            description=table_data.get('description'),
            image=table_data.get('image')
        )
        
        db.add(table)
        db.commit()
        db.refresh(table)
        
        return {
            'success': True,
            'message': 'Столик успешно добавлен',
            'data': table.to_dict()
        }, 201
    
    except IntegrityError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при добавлении столика: такой столик уже существует',
            'error': str(e)
        }, 400
    
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при добавлении столика',
            'error': str(e)
        }, 500

# @desc    Получение всех столиков
# @route   GET /api/tables
# @access  Public
def get_all_tables():
    db = get_db()
    try:
        tables = db.query(Table).order_by(Table.table_number).all()
        
        return {
            'success': True,
            'count': len(tables),
            'data': [table.to_dict() for table in tables]
        }
    except SQLAlchemyError as e:
        return {
            'success': False,
            'message': 'Ошибка при получении столиков',
            'error': str(e)
        }, 500

# @desc    Получение столика по ID
# @route   GET /api/tables/:id
# @access  Public
def get_table_by_id(table_id):
    db = get_db()
    
    try:
        table = db.query(Table).filter(Table.id == table_id).first()
        
        if not table:
            return {
                'success': False,
                'message': 'Столик не найден'
            }, 404
        
        return {
            'success': True,
            'data': table.to_dict()
        }
    except SQLAlchemyError as e:
        return {
            'success': False,
            'message': 'Ошибка при получении столика',
            'error': str(e)
        }, 500

# @desc    Обновление столика
# @route   PUT /api/tables/:id
# @access  Private/Admin
def update_table(table_id, table_data):
    db = get_db()
    
    try:
        table = db.query(Table).filter(Table.id == table_id).first()
        
        if not table:
            return {
                'success': False,
                'message': 'Столик не найден'
            }, 404
        
        # Обновляем поля столика
        if 'table_number' in table_data:
            # Проверка уникальности номера, если он изменяется
            if table_data['table_number'] != table.table_number:
                existing_table = db.query(Table).filter(Table.table_number == table_data['table_number']).first()
                if existing_table:
                    return {
                        'success': False,
                        'message': 'Столик с таким номером уже существует'
                    }, 400
            table.table_number = table_data['table_number']
            
        if 'capacity' in table_data:
            table.capacity = table_data['capacity']
        if 'location' in table_data:
            table.location = table_data['location']
        if 'is_available' in table_data:
            table.is_available = table_data['is_available']
        if 'description' in table_data:
            table.description = table_data['description']
        if 'image' in table_data:
            table.image = table_data['image']
        
        db.commit()
        db.refresh(table)
        
        return {
            'success': True,
            'message': 'Столик успешно обновлен',
            'data': table.to_dict()
        }
    
    except IntegrityError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при обновлении столика: нарушение уникальности',
            'error': str(e)
        }, 400
    
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при обновлении столика',
            'error': str(e)
        }, 500

# @desc    Удаление столика
# @route   DELETE /api/tables/:id
# @access  Private/Admin
def delete_table(table_id):
    db = get_db()
    
    try:
        table = db.query(Table).filter(Table.id == table_id).first()
        
        if not table:
            return {
                'success': False,
                'message': 'Столик не найден'
            }, 404
        
        # Проверяем, есть ли бронирования для этого столика
        if table.reservations and len(table.reservations) > 0:
            return {
                'success': False,
                'message': 'Невозможно удалить столик, для которого есть бронирования'
            }, 400
        
        db.delete(table)
        db.commit()
        
        return {
            'success': True,
            'message': 'Столик успешно удален'
        }
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при удалении столика',
            'error': str(e)
        }, 500 