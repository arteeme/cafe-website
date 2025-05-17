// Основные функции для взаимодействия с API

// Получение меню
async function getMenu() {
    try {
        console.log('Запрос меню - начало');
        const response = await fetch('/api/menu');
        console.log('Запрос меню - ответ получен:', response.status);
        const data = await response.json();
        console.log('Данные меню:', data);
        return data.data || [];
    } catch (error) {
        console.error('Ошибка при получении меню:', error);
        return [];
    }
}

// Получение популярных блюд
async function getPopularItems() {
    try {
        const response = await fetch('/api/menu/popular');
        const data = await response.json();
        return data.data || [];
    } catch (error) {
        console.error('Ошибка при получении популярных блюд:', error);
        return [];
    }
}

// Функция для вывода популярных блюд на главной странице
async function displayPopularItems() {
    const popularDishesContainer = document.querySelector('.popular-dishes .row');
    if (!popularDishesContainer) return;

    // Очистить контейнер
    popularDishesContainer.innerHTML = '';

    try {
        const items = await getPopularItems();
        
        if (items.length === 0) {
            // Если данных нет, используем заглушки
            const placeholderItems = [
                {
                    name: 'Фирменный борщ',
                    description: 'Насыщенный ароматный борщ с говядиной, подается со сметаной и пампушками с чесноком.',
                    price: 350,
                    image: 'images/dish1.jpg'
                },
                {
                    name: 'Пельмени домашние',
                    description: 'Сочные домашние пельмени из свинины и говядины, подаются со сметаной.',
                    price: 420,
                    image: 'images/dish2.jpg'
                },
                {
                    name: 'Медовик',
                    description: 'Нежный слоеный торт с медовыми коржами и кремом из сметаны.',
                    price: 280,
                    image: 'images/dish3.jpg'
                }
            ];
            
            renderMenuItems(placeholderItems, popularDishesContainer);
            return;
        }
        
        renderMenuItems(items, popularDishesContainer);
    } catch (error) {
        console.error('Ошибка при отображении популярных блюд:', error);
    }
}

// Функция для отображения меню на странице menu.html
async function displayMenu() {
    const menuContainer = document.getElementById('menu-container');
    if (!menuContainer) return;

    try {
        const items = await getMenu();
        
        if (items.length === 0) {
            menuContainer.innerHTML = '<p class="text-center">Меню временно недоступно.</p>';
            return;
        }
        
        // Группировка по категориям
        const categories = {};
        items.forEach(item => {
            if (!categories[item.category]) {
                categories[item.category] = [];
            }
            categories[item.category].push(item);
        });
        
        // Вывод блюд по категориям
        for (const [category, categoryItems] of Object.entries(categories)) {
            const categorySection = document.createElement('div');
            categorySection.classList.add('menu-category', 'mb-5');
            
            categorySection.innerHTML = `
                <h3 class="mb-4">${formatCategory(category)}</h3>
                <div class="row"></div>
            `;
            
            const categoryRow = categorySection.querySelector('.row');
            renderMenuItems(categoryItems, categoryRow);
            
            menuContainer.appendChild(categorySection);
        }
    } catch (error) {
        console.error('Ошибка при отображении меню:', error);
        menuContainer.innerHTML = '<p class="text-center">Ошибка при загрузке меню. Попробуйте позже.</p>';
    }
}

// Функция для форматирования названия категории
function formatCategory(category) {
    const categoryMap = {
        'завтрак': 'Завтраки',
        'суп': 'Супы',
        'основное': 'Основные блюда',
        'десерт': 'Десерты',
        'напиток': 'Напитки',
        'специальное': 'Специальные предложения'
    };
    
    return categoryMap[category] || category.charAt(0).toUpperCase() + category.slice(1);
}

// Вспомогательная функция для отрисовки элементов меню
function renderMenuItems(items, container) {
    items.forEach(item => {
        const col = document.createElement('div');
        col.classList.add('col-md-4', 'mb-4');
        
        col.innerHTML = `
            <div class="card h-100">
                <img src="${item.image || 'images/placeholder.jpg'}" class="card-img-top" alt="${item.name}">
                <div class="card-body">
                    <h5 class="card-title">${item.name}</h5>
                    <p class="card-text">${item.description}</p>
                    <p class="fw-bold">${item.price} ₽</p>
                </div>
            </div>
        `;
        
        container.appendChild(col);
    });
}

// Функция для отправки брони столика
async function reserveTable(formData) {
    try {
        const response = await fetch('/api/tables/reserve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        return await response.json();
    } catch (error) {
        console.error('Ошибка при бронировании:', error);
        return { success: false, message: 'Произошла ошибка при отправке запроса.' };
    }
}

// Обработка формы бронирования
function setupReservationForm() {
    const form = document.getElementById('reservation-form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            name: form.querySelector('#name').value,
            phone: form.querySelector('#phone').value,
            date: form.querySelector('#date').value,
            time: form.querySelector('#time').value,
            guests: form.querySelector('#guests').value,
            requests: form.querySelector('#requests')?.value || ''
        };
        
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = 'Отправка...';
        
        try {
            const result = await reserveTable(formData);
            if (result.success) {
                alert('Бронирование успешно отправлено! Мы свяжемся с вами для подтверждения.');
                form.reset();
            } else {
                alert(result.message || 'Ошибка при бронировании. Попробуйте позже.');
            }
        } catch (error) {
            alert('Произошла ошибка. Пожалуйста, попробуйте позже.');
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    });
}

// Функции для главной страницы

// Загрузка популярных блюд
async function loadPopularItems() {
    const popularItemsContainer = document.getElementById('popular-items-container');
    if (!popularItemsContainer) return;

    try {
        const response = await fetch('/api/menu/popular');
        const data = await response.json();

        if (data.success && data.data && data.data.length > 0) {
            // Очищаем контейнер
            popularItemsContainer.innerHTML = '';
            
            // Создаем карточки для каждого популярного блюда
            data.data.forEach(item => {
                const col = document.createElement('div');
                col.className = 'col-md-4 mb-4';
                
                col.innerHTML = `
                    <div class="card h-100 shadow-sm">
                        <img src="${item.image || '/images/placeholder.jpg'}" class="card-img-top" alt="${item.name}">
                        <div class="card-body">
                            <h5 class="card-title">${item.name}</h5>
                            <p class="card-text">${item.description.substring(0, 100)}${item.description.length > 100 ? '...' : ''}</p>
                            <div class="d-flex justify-content-between align-items-center mt-3">
                                <span class="fw-bold">${item.price} ₽</span>
                                <button class="btn btn-primary add-to-cart-btn" 
                                    data-id="${item.id}" 
                                    data-name="${item.name}" 
                                    data-price="${item.price}" 
                                    data-image="${item.image || '/images/placeholder.jpg'}">
                                    В корзину
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                
                popularItemsContainer.appendChild(col);
            });
            
            // Добавляем обработчики для кнопок "В корзину"
            setupAddToCartButtons();
        } else {
            throw new Error('Нет данных о популярных блюдах');
        }
    } catch (error) {
        console.error('Ошибка при загрузке популярных блюд:', error);
        popularItemsContainer.innerHTML = `
            <div class="col-12 text-center">
                <p>Не удалось загрузить популярные блюда. Попробуйте позже.</p>
                <a href="/menu" class="btn btn-primary mt-2">Перейти в меню</a>
            </div>
        `;
    }
}

// Настройка обработчиков событий
function setupPageEventListeners() {
    // Здесь можно добавить обработчики событий для элементов на главной странице
    
    // Примеры возможных обработчиков:
    
    // Анимация прокрутки для якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Проверка, поддерживает ли браузер CSS custom properties
function supportsCSSVars() {
    return window.CSS && CSS.supports('color', 'var(--test)');
}

// Применение стилей для баннера
function setupBanner() {
    const banner = document.querySelector('.main-banner');
    if (banner) {
        banner.style.backgroundImage = 'linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url("/images/cafe-banner.jpg")';
        banner.style.backgroundSize = 'cover';
        banner.style.backgroundPosition = 'center';
        banner.style.minHeight = '500px';
        banner.style.display = 'flex';
        banner.style.alignItems = 'center';
    }
}

// Инициализация страницы
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, находимся ли мы на главной странице
    if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
        // Загружаем популярные блюда
        loadPopularItems();
        
        // Настраиваем обработчики событий
        setupPageEventListeners();
        
        // Настраиваем стили для баннера
        setupBanner();
    }
    
    // Обновляем UI в зависимости от статуса авторизации (если auth.js загружен)
    if (typeof updateAuthUI === 'function') {
        updateAuthUI();
    }
}); 