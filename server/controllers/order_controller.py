from models import Order, OrderItem, MenuItem
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from db import SessionLocal
from flask_jwt_extended import get_jwt_identity
import datetime

# Вспомогательная функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# @desc    Создание нового заказа
# @route   POST /api/orders
# @access  Private
def create_order(order_data):
    db = get_db()
    try:
        user_id = get_jwt_identity()
        
        # Проверка наличия элементов заказа
        items = order_data.get('items', [])
        if not items or len(items) == 0:
            return {
                'success': False,
                'message': 'Заказ должен содержать хотя бы один элемент'
            }, 400
        
        # Создаем заказ
        order = Order(
            user_id=user_id,
            total_amount=order_data.get('total_amount'),
            order_type=order_data.get('order_type'),
            payment_method=order_data.get('payment_method'),
            phone=order_data.get('phone'),
            name=order_data.get('name'),
            address=order_data.get('address'),
            comment=order_data.get('comment')
        )
        
        db.add(order)
        db.flush()  # Получаем ID заказа до коммита
        
        # Добавляем позиции заказа
        for item_data in items:
            menu_item = db.query(MenuItem).filter(MenuItem.id == item_data.get('menu_item_id')).first()
            if not menu_item:
                db.rollback()
                return {
                    'success': False,
                    'message': f'Элемент меню с ID {item_data.get("menu_item_id")} не найден'
                }, 404
            
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                quantity=item_data.get('quantity'),
                price=menu_item.price,
                notes=item_data.get('notes')
            )
            db.add(order_item)
        
        db.commit()
        db.refresh(order)
        
        return {
            'success': True,
            'message': 'Заказ успешно создан',
            'data': order.to_dict()
        }, 201
        
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при создании заказа',
            'error': str(e)
        }, 500

# @desc    Получение всех заказов (для админа)
# @route   GET /api/orders
# @access  Private/Admin
def get_all_orders():
    db = get_db()
    try:
        orders = db.query(Order).order_by(Order.created_at.desc()).all()
        
        return {
            'success': True,
            'count': len(orders),
            'data': [order.to_dict() for order in orders]
        }
    except SQLAlchemyError as e:
        return {
            'success': False,
            'message': 'Ошибка при получении заказов',
            'error': str(e)
        }, 500

# @desc    Получение заказов пользователя
# @route   GET /api/orders/my
# @access  Private
def get_my_orders():
    user_id = get_jwt_identity()
    db = get_db()
    
    try:
        orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()
        
        return {
            'success': True,
            'count': len(orders),
            'data': [order.to_dict() for order in orders]
        }
    except SQLAlchemyError as e:
        return {
            'success': False,
            'message': 'Ошибка при получении заказов',
            'error': str(e)
        }, 500

# @desc    Получение заказа по ID
# @route   GET /api/orders/:id
# @access  Private
def get_order_by_id(order_id):
    user_id = get_jwt_identity()
    db = get_db()
    
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return {
                'success': False,
                'message': 'Заказ не найден'
            }, 404
        
        # Проверка прав (пользователь может видеть только свои заказы)
        if order.user_id != user_id:
            return {
                'success': False,
                'message': 'У вас нет прав для просмотра этого заказа'
            }, 403
        
        return {
            'success': True,
            'data': order.to_dict()
        }
    except SQLAlchemyError as e:
        return {
            'success': False,
            'message': 'Ошибка при получении заказа',
            'error': str(e)
        }, 500

# @desc    Обновление статуса заказа
# @route   PUT /api/orders/:id/status
# @access  Private/Admin
def update_order_status(order_id, status_data):
    db = get_db()
    
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return {
                'success': False,
                'message': 'Заказ не найден'
            }, 404
        
        new_status = status_data.get('status')
        if not new_status:
            return {
                'success': False,
                'message': 'Необходимо указать новый статус'
            }, 400
        
        # Обновляем статус
        order.status = new_status
        
        # Если статус "доставлен" или "получен", устанавливаем время завершения
        if new_status in ['доставлен', 'получен']:
            order.completed_at = datetime.datetime.now()
        
        db.commit()
        db.refresh(order)
        
        return {
            'success': True,
            'message': 'Статус заказа успешно обновлен',
            'data': order.to_dict()
        }
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при обновлении статуса заказа',
            'error': str(e)
        }, 500

# @desc    Отмена заказа пользователем
# @route   PUT /api/orders/:id/cancel
# @access  Private
def cancel_order(order_id):
    user_id = get_jwt_identity()
    db = get_db()
    
    try:
        order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
        
        if not order:
            return {
                'success': False,
                'message': 'Заказ не найден или у вас нет прав для его отмены'
            }, 404
        
        # Проверка: можно отменить только заказы в определенных статусах
        if order.status not in ['новый', 'подтвержден']:
            return {
                'success': False,
                'message': 'Нельзя отменить заказ в статусе "' + order.status + '"'
            }, 400
        
        # Обновляем статус
        order.status = 'отменен'
        order.cancelled_at = datetime.datetime.now()
        
        db.commit()
        db.refresh(order)
        
        return {
            'success': True,
            'message': 'Заказ успешно отменен',
            'data': order.to_dict()
        }
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при отмене заказа',
            'error': str(e)
        }, 500

# @desc    Получение истории заказов пользователя
# @route   GET /api/orders/history
# @access  Private
def get_user_orders():
    user_id = get_jwt_identity()
    db = get_db()
    
    try:
        # Получаем заказы пользователя, отсортированные по дате (новые вверху)
        orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()
        
        # Преобразуем в формат, который ожидает фронтенд
        formatted_orders = []
        for order in orders:
            # Получаем элементы заказа
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            
            items_data = []
            for item in order_items:
                menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
                if menu_item:
                    items_data.append({
                        'id': menu_item.id,
                        'name': menu_item.name,
                        'price': item.price,
                        'quantity': item.quantity,
                        'image': menu_item.image
                    })
            
            # Формируем объект заказа
            formatted_order = {
                'id': order.id,
                'order_number': f"{order.id:06d}",  # Форматированный номер заказа
                'status': order.status,
                'created_at': order.created_at.isoformat(),
                'total_amount': order.total_amount,
                'order_type': order.order_type,
                'address': order.address,
                'payment_status': 'оплачен' if order.is_paid else 'не оплачен',
                'payment_method': order.payment_method,
                'comment': order.comment,
                'items': items_data
            }
            
            formatted_orders.append(formatted_order)
        
        return {
            'success': True,
            'orders': formatted_orders
        }
    except SQLAlchemyError as e:
        return {
            'success': False,
            'message': 'Ошибка при получении истории заказов',
            'error': str(e)
        }, 500 