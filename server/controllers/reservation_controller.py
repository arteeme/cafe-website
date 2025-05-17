from models import Reservation, Table
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, func, or_
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

# @desc    Создание нового бронирования
# @route   POST /api/reservations
# @access  Private
def create_reservation(reservation_data):
    db = get_db()
    try:
        user_id = get_jwt_identity()
        table_id = reservation_data.get('table_id')
        reservation_date = datetime.datetime.strptime(reservation_data.get('reservation_date'), '%Y-%m-%d').date()
        reservation_time = datetime.datetime.strptime(reservation_data.get('reservation_time'), '%H:%M').time()
        guests_count = reservation_data.get('guests_count')
        duration = reservation_data.get('duration', 120)
        special_requests = reservation_data.get('special_requests')
        
        # Проверка доступности столика
        table = db.query(Table).filter(Table.id == table_id).first()
        if not table:
            return {
                'success': False,
                'message': 'Столик не найден'
            }, 404
        
        # Проверка количества гостей
        if guests_count > table.capacity:
            return {
                'success': False,
                'message': f'Столик вмещает максимум {table.capacity} гостей'
            }, 400
        
        # Проверка, доступен ли столик в указанное время
        reserved_time_start = datetime.datetime.combine(reservation_date, reservation_time)
        reserved_time_end = reserved_time_start + datetime.timedelta(minutes=duration)
        
        # Ищем другие бронирования на этот столик в пересекающийся интервал времени
        existing_reservations = db.query(Reservation).filter(
            and_(
                Reservation.table_id == table_id,
                Reservation.reservation_date == reservation_date,
                Reservation.status.in_(['ожидание', 'подтверждено']),
                or_(
                    # Начало нового бронирования попадает в интервал существующего
                    and_(
                        func.time(Reservation.reservation_time) <= reservation_time,
                        func.addtime(Reservation.reservation_time, func.sec_to_time(Reservation.duration * 60)) >= reservation_time
                    ),
                    # Конец нового бронирования попадает в интервал существующего
                    and_(
                        func.time(Reservation.reservation_time) <= reserved_time_end.time(),
                        func.addtime(Reservation.reservation_time, func.sec_to_time(Reservation.duration * 60)) >= reserved_time_end.time()
                    ),
                    # Новое бронирование полностью включает существующее
                    and_(
                        func.time(Reservation.reservation_time) >= reservation_time,
                        func.addtime(Reservation.reservation_time, func.sec_to_time(Reservation.duration * 60)) <= reserved_time_end.time()
                    )
                )
            )
        ).all()
        
        if existing_reservations:
            return {
                'success': False,
                'message': 'Столик уже забронирован на указанное время'
            }, 400
        
        # Создаем бронирование
        reservation = Reservation(
            user_id=user_id,
            table_id=table_id,
            reservation_date=reservation_date,
            reservation_time=reservation_time,
            guests_count=guests_count,
            duration=duration,
            special_requests=special_requests
        )
        
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        
        return {
            'success': True,
            'message': 'Бронирование успешно создано',
            'data': reservation.to_dict()
        }, 201
        
    except ValueError as e:
        return {
            'success': False,
            'message': 'Некорректный формат даты или времени',
            'error': str(e)
        }, 400
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при создании бронирования',
            'error': str(e)
        }, 500

# @desc    Получение всех бронирований (для админа)
# @route   GET /api/reservations
# @access  Private/Admin
def get_all_reservations():
    db = get_db()
    try:
        reservations = db.query(Reservation).order_by(Reservation.reservation_date.desc()).all()
        
        return {
            'success': True,
            'count': len(reservations),
            'data': [reservation.to_dict() for reservation in reservations]
        }
    except SQLAlchemyError as e:
        return {
            'success': False,
            'message': 'Ошибка при получении бронирований',
            'error': str(e)
        }, 500

# @desc    Получение бронирований пользователя
# @route   GET /api/reservations/my
# @access  Private
def get_my_reservations():
    user_id = get_jwt_identity()
    db = get_db()
    
    try:
        reservations = db.query(Reservation).filter(Reservation.user_id == user_id).order_by(Reservation.reservation_date.desc()).all()
        
        return {
            'success': True,
            'count': len(reservations),
            'data': [reservation.to_dict() for reservation in reservations]
        }
    except SQLAlchemyError as e:
        return {
            'success': False,
            'message': 'Ошибка при получении бронирований',
            'error': str(e)
        }, 500

# @desc    Получение бронирования по ID
# @route   GET /api/reservations/:id
# @access  Private
def get_reservation_by_id(reservation_id):
    db = get_db()
    try:
        user_id = get_jwt_identity()
        
        # Находим бронирование
        reservation = db.query(Reservation).filter(
            Reservation.id == reservation_id
        ).first()
        
        # Проверяем существование
        if not reservation:
            return {
                'success': False,
                'message': 'Бронирование не найдено'
            }, 404
        
        # Проверяем принадлежность пользователю
        if reservation.user_id != user_id:
            return {
                'success': False,
                'message': 'Доступ запрещен'
            }, 403
        
        return {
            'success': True,
            'data': reservation.to_dict()
        }
    except SQLAlchemyError as e:
        return {
            'success': False,
            'message': 'Ошибка при получении бронирования',
            'error': str(e)
        }, 500

# @desc    Обновление статуса бронирования
# @route   PUT /api/reservations/:id/status
# @access  Private/Admin
def update_reservation_status(reservation_id, status_data):
    db = get_db()
    
    try:
        reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
        
        if not reservation:
            return {
                'success': False,
                'message': 'Бронирование не найдено'
            }, 404
        
        new_status = status_data.get('status')
        if not new_status:
            return {
                'success': False,
                'message': 'Необходимо указать новый статус'
            }, 400
        
        # Обновляем статус
        reservation.status = new_status
        db.commit()
        db.refresh(reservation)
        
        return {
            'success': True,
            'message': 'Статус бронирования успешно обновлен',
            'data': reservation.to_dict()
        }
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при обновлении статуса бронирования',
            'error': str(e)
        }, 500

# @desc    Отмена бронирования
# @route   DELETE /api/reservations/:id
# @access  Private
def cancel_reservation(reservation_id):
    db = get_db()
    try:
        user_id = get_jwt_identity()
        
        # Находим бронирование
        reservation = db.query(Reservation).filter(
            Reservation.id == reservation_id
        ).first()
        
        # Проверяем существование
        if not reservation:
            return {
                'success': False,
                'message': 'Бронирование не найдено'
            }, 404
        
        # Проверяем принадлежность пользователю
        if reservation.user_id != user_id:
            return {
                'success': False,
                'message': 'Доступ запрещен'
            }, 403
        
        # Проверяем возможность отмены (нельзя отменять завершенные)
        if reservation.status in ['завершено', 'отменено']:
            return {
                'success': False,
                'message': f'Невозможно отменить бронирование в статусе "{reservation.status}"'
            }, 400
        
        # Меняем статус на "отменено"
        reservation.status = 'отменено'
        db.commit()
        
        return {
            'success': True,
            'message': 'Бронирование успешно отменено'
        }
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при отмене бронирования',
            'error': str(e)
        }, 500

# @desc    Проверка доступных столиков
# @route   GET /api/reservations/available
# @access  Public
def get_available_tables(date, time, guests):
    db = get_db()
    try:
        # Преобразуем параметры
        reservation_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        reservation_time = datetime.datetime.strptime(time, '%H:%M').time()
        guests_count = int(guests)
        
        # Находим все столики с подходящей вместимостью
        suitable_tables = db.query(Table).filter(Table.capacity >= guests_count).all()
        
        if not suitable_tables:
            return {
                'success': False,
                'message': 'Нет столиков с подходящей вместимостью'
            }, 404
        
        # Проверяем, какие из них свободны в указанное время
        available_tables = []
        
        for table in suitable_tables:
            # Ищем бронирования для данного столика на указанную дату
            conflicting_reservations = db.query(Reservation).filter(
                and_(
                    Reservation.table_id == table.id,
                    Reservation.reservation_date == reservation_date,
                    Reservation.status.in_(['ожидание', 'подтверждено'])
                )
            ).all()
            
            # Проверяем, есть ли конфликты по времени
            has_conflict = False
            for res in conflicting_reservations:
                res_start = datetime.datetime.combine(reservation_date, res.reservation_time)
                res_end = res_start + datetime.timedelta(minutes=res.duration)
                
                new_start = datetime.datetime.combine(reservation_date, reservation_time)
                new_end = new_start + datetime.timedelta(minutes=120)  # по умолчанию 2 часа
                
                # Проверка пересечения интервалов
                if (new_start < res_end) and (res_start < new_end):
                    has_conflict = True
                    break
            
            if not has_conflict:
                available_tables.append(table.to_dict())
        
        return {
            'success': True,
            'count': len(available_tables),
            'data': available_tables
        }
    except ValueError as e:
        return {
            'success': False,
            'message': 'Некорректный формат даты или времени',
            'error': str(e)
        }, 400
    except SQLAlchemyError as e:
        return {
            'success': False,
            'message': 'Ошибка при проверке доступных столиков',
            'error': str(e)
        }, 500

# @desc    Получение всех бронирований пользователя
# @route   GET /api/reservations
# @access  Private
def get_user_reservations():
    db = get_db()
    try:
        user_id = get_jwt_identity()
        
        # Получаем все бронирования пользователя, сортируем по дате (сначала новые)
        reservations = db.query(Reservation).filter(
            Reservation.user_id == user_id
        ).order_by(Reservation.reservation_date.desc(), Reservation.reservation_time.desc()).all()
        
        return {
            'success': True,
            'count': len(reservations),
            'data': [reservation.to_dict() for reservation in reservations]
        }
    except SQLAlchemyError as e:
        return {
            'success': False,
            'message': 'Ошибка при получении бронирований',
            'error': str(e)
        }, 500

# @desc    Обновление бронирования
# @route   PUT /api/reservations/:id
# @access  Private
def update_reservation(reservation_id, reservation_data):
    db = get_db()
    try:
        user_id = get_jwt_identity()
        
        # Находим бронирование
        reservation = db.query(Reservation).filter(
            Reservation.id == reservation_id
        ).first()
        
        # Проверяем существование
        if not reservation:
            return {
                'success': False,
                'message': 'Бронирование не найдено'
            }, 404
        
        # Проверяем принадлежность пользователю
        if reservation.user_id != user_id:
            return {
                'success': False,
                'message': 'Доступ запрещен'
            }, 403
        
        # Проверяем возможность изменения (нельзя менять завершенные или отмененные)
        if reservation.status not in ['ожидание', 'подтверждено']:
            return {
                'success': False,
                'message': f'Невозможно изменить бронирование в статусе "{reservation.status}"'
            }, 400
        
        # Обновляем данные, если они предоставлены
        if 'reservation_date' in reservation_data:
            reservation.reservation_date = datetime.datetime.strptime(
                reservation_data.get('reservation_date'), '%Y-%m-%d'
            ).date()
        
        if 'reservation_time' in reservation_data:
            reservation.reservation_time = datetime.datetime.strptime(
                reservation_data.get('reservation_time'), '%H:%M'
            ).time()
        
        if 'guests_count' in reservation_data:
            reservation.guests_count = reservation_data.get('guests_count')
        
        if 'duration' in reservation_data:
            reservation.duration = reservation_data.get('duration')
        
        if 'special_requests' in reservation_data:
            reservation.special_requests = reservation_data.get('special_requests')
        
        # Если меняем столик, проверяем его доступность
        if 'table_id' in reservation_data and reservation_data.get('table_id') != reservation.table_id:
            table_id = reservation_data.get('table_id')
            table = db.query(Table).filter(Table.id == table_id).first()
            
            if not table:
                return {
                    'success': False,
                    'message': 'Указанный столик не найден'
                }, 404
            
            # Проверяем доступность столика в указанное время
            # ... здесь должна быть логика проверки доступности ...
            
            reservation.table_id = table_id
        
        db.commit()
        db.refresh(reservation)
        
        return {
            'success': True,
            'message': 'Бронирование успешно обновлено',
            'data': reservation.to_dict()
        }
    except ValueError as e:
        return {
            'success': False,
            'message': 'Некорректный формат даты или времени',
            'error': str(e)
        }, 400
    except SQLAlchemyError as e:
        db.rollback()
        return {
            'success': False,
            'message': 'Ошибка при обновлении бронирования',
            'error': str(e)
        }, 500 