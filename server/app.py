from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from config.config import get_config
from db import engine, Base, get_db
from models import create_tables

# Импорт контроллеров
from controllers import menu_controller, user_controller, order_controller
from controllers import table_controller, reservation_controller
# Commented out controllers that don't exist yet
# from controllers import review_controller, contact_controller

# Создаем экземпляр Flask и загружаем конфигурацию
app = Flask(__name__, static_folder='static')
config = get_config()
app.config.from_object(config)

# Добавляем расширения
CORS(app)
jwt = JWTManager(app)

# Инициализируем базу данных при запуске приложения
with app.app_context():
    create_tables()

# Обработка статических файлов
@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(app.static_folder, 'js'), filename)

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(app.static_folder, 'css'), filename)

@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(os.path.join(app.static_folder, 'images'), filename)

# Маршруты для статических HTML страниц
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/menu')
def menu_page():
    return send_from_directory('static', 'menu.html')

@app.route('/about')
def about_page():
    return send_from_directory('static', 'about.html')

@app.route('/contact')
def contact_page():
    return send_from_directory('static', 'contact.html')

@app.route('/login')
def login_page():
    return send_from_directory('static', 'login.html')

@app.route('/profile')
def profile_page():
    return send_from_directory('static', 'profile.html')

@app.route('/reservation')
def reservation_page():
    return send_from_directory('static', 'reservation.html')

@app.route('/cart')
def cart_page():
    return send_from_directory('static', 'cart.html')

@app.route('/checkout')
def checkout_page():
    return send_from_directory('static', 'checkout.html')

# Маршруты API для меню
@app.route('/api/menu', methods=['GET'])
def get_menu():
    return jsonify(menu_controller.get_menu_items())

@app.route('/api/menu/<int:item_id>', methods=['GET'])
def get_menu_item(item_id):
    return jsonify(menu_controller.get_menu_item(item_id))

@app.route('/api/menu', methods=['POST'])
def create_menu_item():
    return jsonify(menu_controller.create_menu_item(request.json))

@app.route('/api/menu/<int:item_id>', methods=['PUT'])
def update_menu_item(item_id):
    return jsonify(menu_controller.update_menu_item(item_id, request.json))

@app.route('/api/menu/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    return jsonify(menu_controller.delete_menu_item(item_id))

@app.route('/api/menu/popular', methods=['GET'])
def get_popular_menu_items():
    return jsonify(menu_controller.get_popular_items())

@app.route('/api/menu/category/<string:category>', methods=['GET'])
def get_category_menu_items(category):
    return jsonify(menu_controller.get_items_by_category(category))

@app.route('/api/menu/search', methods=['GET'])
def search_menu():
    query = request.args.get('q', '')
    return jsonify(menu_controller.search_menu_items(query))

# Маршруты API для аутентификации
@app.route('/api/auth/register', methods=['POST'])
def register():
    result, status_code = user_controller.register_user(request.json)
    return jsonify(result), status_code

@app.route('/api/auth/login', methods=['POST'])
def login():
    result, status_code = user_controller.login_user(request.json)
    return jsonify(result), status_code

@app.route('/api/auth/me', methods=['GET'])
def get_me():
    return jsonify(user_controller.get_current_user())

@app.route('/api/auth/me', methods=['PUT'])
def update_me():
    return jsonify(user_controller.update_user(request.json))

@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    return jsonify(user_controller.forgot_password(request.json))

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    return jsonify(user_controller.reset_password(request.json))

# Маршруты API для заказов
@app.route('/api/orders', methods=['POST'])
def create_order():
    return jsonify(order_controller.create_order(request.json))

@app.route('/api/orders/history', methods=['GET'])
def get_order_history():
    return jsonify(order_controller.get_user_orders())

# Маршруты API для избранных блюд
@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    return jsonify(user_controller.get_favorites())

@app.route('/api/favorites/<int:item_id>', methods=['POST'])
def add_favorite(item_id):
    return jsonify(user_controller.add_favorite(item_id))

@app.route('/api/favorites/<int:item_id>', methods=['DELETE'])
def remove_favorite(item_id):
    return jsonify(user_controller.remove_favorite(item_id))

# Маршруты API для адресов доставки
@app.route('/api/addresses', methods=['GET'])
def get_addresses():
    return jsonify(user_controller.get_addresses())

@app.route('/api/addresses', methods=['POST'])
def add_address():
    return jsonify(user_controller.add_address(request.json))

@app.route('/api/addresses/<int:address_id>', methods=['PUT'])
def update_address(address_id):
    return jsonify(user_controller.update_address(address_id, request.json))

@app.route('/api/addresses/<int:address_id>', methods=['DELETE'])
def delete_address(address_id):
    return jsonify(user_controller.delete_address(address_id))

# Маршруты API для столиков и бронирования
@app.route('/api/tables', methods=['GET'])
def get_tables():
    date = request.args.get('date')
    start_time = request.args.get('startTime')
    end_time = request.args.get('endTime')
    guests_count = request.args.get('guestsCount')
    
    if date and start_time and guests_count:
        return jsonify(reservation_controller.get_available_tables(date, start_time, guests_count))
    else:
        return jsonify(table_controller.get_all_tables())

@app.route('/api/tables/<int:table_id>', methods=['GET'])
def get_table(table_id):
    return jsonify(table_controller.get_table_by_id(table_id))

@app.route('/api/tables/reserve', methods=['POST'])
def reserve_table():
    return jsonify(reservation_controller.create_reservation(request.json))

@app.route('/api/reservations', methods=['GET'])
def get_user_reservations():
    return jsonify(reservation_controller.get_user_reservations())

@app.route('/api/reservations/<int:reservation_id>', methods=['GET'])
def get_reservation(reservation_id):
    return jsonify(reservation_controller.get_reservation_by_id(reservation_id))

@app.route('/api/reservations/<int:reservation_id>', methods=['PUT'])
def update_reservation(reservation_id):
    return jsonify(reservation_controller.update_reservation(reservation_id, request.json))

@app.route('/api/reservations/<int:reservation_id>', methods=['DELETE'])
def cancel_reservation(reservation_id):
    return jsonify(reservation_controller.cancel_reservation(reservation_id))

# Маршруты API для промокодов
@app.route('/api/promo/check', methods=['GET'])
def check_promo():
    code = request.args.get('code', '')
    subtotal = float(request.args.get('subtotal', 0))
    return jsonify({
        'success': True,
        'message': 'Промокод применен',
        'discount': int(subtotal * 0.1)  # 10% скидка
    })

# Обработка ошибок
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Ресурс не найден'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'success': False, 'message': 'Внутренняя ошибка сервера'}), 500

# Обслуживание статических файлов
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# Обработка всех остальных маршрутов (для SPA)
@app.route('/<path:path>')
def serve_spa(path):
    # Проверяем, является ли путь API запросом
    if path.startswith('api/'):
        return not_found(None)
    
    # Пробуем отдать статический HTML файл
    html_file = path
    if not html_file.endswith('.html'):
        html_file += '.html'
    
    if os.path.exists(os.path.join(app.static_folder, html_file)):
        return send_from_directory('static', html_file)
    
    # Если запрос на файл в папке js, css или images
    if any(path.startswith(folder) for folder in ['js/', 'css/', 'images/']):
        # Если файл существует, отдаем его
        if os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory('static', path)
    
    # Если не нашли, отдаем index.html (для маршрутов SPA)
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=config.DEBUG) 