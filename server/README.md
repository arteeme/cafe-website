# Web-сайт кафе на Flask + SQLAlchemy

API сервер для веб-сайта кафе, написанный на Python с использованием Flask и SQLAlchemy с базой данных SQLite.

## Технологии

- Python 3.8+
- Flask - веб-фреймворк
- SQLAlchemy - ORM для работы с базами данных
- JWT - для аутентификации
- SQLite - легкая встроенная база данных (по умолчанию)
- MySQL - опциональная база данных для продакшн-использования

## Подготовка и установка проекта

### Требования

- Python 3.8+
- pip (менеджер пакетов Python)

### Шаг 1: Клонирование репозитория

```bash
git clone <url-репозитория>
cd WebSiteCafe
```

### Шаг 2: Настройка виртуального окружения Python

```bash
# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Шаг 3: Установка зависимостей

```bash
cd server
pip install -r requirements.txt
```

## Запуск проекта

### Запуск сервера с SQLite (по умолчанию)

SQLite настроен по умолчанию и не требует дополнительной настройки:

```bash
cd server
python app.py
```

После запуска сервер будет доступен по адресу:
- **http://localhost:5000** - основной интерфейс
- **http://localhost:5000/api/menu** - API для получения меню

### Запуск фронтенда

Если у вас есть собранная версия клиентского интерфейса:

1. Откройте в браузере адрес: **http://localhost:5000**
2. Если веб-интерфейс доступен, вы увидите главную страницу кафе

## Переключение на MySQL (опционально)

Если вы хотите использовать MySQL вместо SQLite:

1. Установите и запустите MySQL сервер
2. Создайте базу данных `cafedb`
3. Отредактируйте файл `server/db.py`, раскомментировав код для MySQL:
   ```python
   # Закомментируйте SQLite настройки
   # DB_PATH = os.path.join(os.path.dirname(__file__), 'cafe.db')
   # DATABASE_URL = f"sqlite:///{DB_PATH}"
   
   # Раскомментируйте MySQL настройки
   DB_HOST = os.getenv('DB_HOST', 'localhost')
   DB_NAME = os.getenv('DB_NAME', 'cafedb')
   DB_USER = os.getenv('DB_USER', 'root')  # Измените на ваше имя пользователя
   DB_PASSWORD = os.getenv('DB_PASSWORD', '') # Укажите ваш пароль
   DB_DIALECT = os.getenv('DB_DIALECT', 'mysql')
   DATABASE_URL = f"{DB_DIALECT}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
   
   # Удалите аргумент connect_args
   engine = create_engine(DATABASE_URL, echo=True)
   ```

4. Создайте файл `.env` в директории `server` со следующими параметрами:
   ```
   DB_HOST=localhost
   DB_NAME=cafedb
   DB_USER=ваш_пользователь
   DB_PASSWORD=ваш_пароль
   DB_DIALECT=mysql
   ```

5. Запустите сервер:
   ```bash
   python app.py
   ```

## Тестирование API

После запуска сервера вы можете протестировать API с помощью:

- Веб-браузера (для GET запросов)
- Postman или другого API-клиента
- curl (для терминала)

### Примеры запросов к API:

1. Получить все пункты меню:
   ```bash
   curl http://localhost:5000/api/menu
   ```

2. Получить популярные блюда:
   ```bash
   curl http://localhost:5000/api/menu/popular
   ```

3. Поиск блюд:
   ```bash
   curl http://localhost:5000/api/menu/search?q=суп
   ```

## Структура проекта

```
server/
├── app.py                 # Основной файл приложения
├── db.py                  # Настройка подключения к БД
├── cafe.db                # SQLite база данных (создается автоматически)
├── config/                # Конфигурационные файлы
├── controllers/           # Контроллеры API
├── models/                # Модели данных SQLAlchemy
└── requirements.txt       # Зависимости проекта
```

## Устранение проблем

1. **Ошибка "Модуль не найден"**: Убедитесь, что вы находитесь в корректной директории и виртуальное окружение активировано.

2. **Ошибка подключения к базе данных**:
   - Если используется SQLite: убедитесь, что у вас есть права на запись в директорию `server/`.
   - Если используется MySQL: проверьте настройки подключения и что MySQL сервер запущен.

3. **Порт уже используется**: Если порт 5000 занят, измените порт в файле `app.py`:
   ```python
   port = int(os.environ.get('PORT', 5001))  # измените на другой номер порта
   ```

## API endpoints

### Меню
- `GET /api/menu` - Получить все пункты меню
- `GET /api/menu/:id` - Получить пункт меню по ID
- `POST /api/menu` - Создать новый пункт меню (только админ)
- `PUT /api/menu/:id` - Обновить пункт меню (только админ)
- `DELETE /api/menu/:id` - Удалить пункт меню (только админ)
- `GET /api/menu/popular` - Получить популярные блюда
- `GET /api/menu/category/:category` - Получить блюда по категории
- `GET /api/menu/search?q=query` - Поиск блюд

### Пользователи
- `POST /api/auth/register` - Регистрация нового пользователя
- `POST /api/auth/login` - Вход в систему
- `GET /api/auth/me` - Получить данные текущего пользователя
- `PUT /api/auth/me` - Обновить данные пользователя

### Заказы
- `POST /api/orders` - Создать новый заказ
- `GET /api/orders` - Получить все заказы пользователя
- `GET /api/orders/:id` - Получить заказ по ID

### Столики
- `GET /api/tables` - Получить все столики
- `POST /api/tables/reserve` - Зарезервировать столик

### Отзывы
- `POST /api/reviews` - Добавить отзыв
- `GET /api/reviews/menu/:menuItemId` - Получить отзывы о блюде

## Лицензия

Этот проект лицензирован по лицензии MIT. 