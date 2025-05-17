// Управление корзиной покупок

// Класс для работы с корзиной покупок
class Cart {
    constructor() {
        this.items = [];
        this.loadFromStorage();
    }
    
    // Загрузка корзины из localStorage
    loadFromStorage() {
        const savedCart = localStorage.getItem('cart');
        if (savedCart) {
            try {
                this.items = JSON.parse(savedCart);
            } catch (e) {
                console.error('Ошибка при загрузке корзины:', e);
                this.items = [];
            }
        }
    }
    
    // Сохранение корзины в localStorage
    saveToStorage() {
        localStorage.setItem('cart', JSON.stringify(this.items));
        this.updateCartUI();
    }
    
    // Добавление товара в корзину
    addItem(item, quantity = 1) {
        // Проверяем, есть ли такой товар уже в корзине
        const existingItemIndex = this.items.findIndex(i => i.id === item.id);
        
        if (existingItemIndex !== -1) {
            // Если товар уже есть, увеличиваем количество
            this.items[existingItemIndex].quantity += quantity;
        } else {
            // Иначе добавляем новый товар
            this.items.push({
                id: item.id,
                name: item.name,
                price: item.price,
                image: item.image,
                quantity: quantity
            });
        }
        
        this.saveToStorage();
    }
    
    // Изменение количества товара в корзине
    updateItemQuantity(itemId, quantity) {
        const itemIndex = this.items.findIndex(item => item.id === itemId);
        
        if (itemIndex !== -1) {
            if (quantity > 0) {
                this.items[itemIndex].quantity = quantity;
            } else {
                // Если количество меньше или равно 0, удаляем товар
                this.removeItem(itemId);
                return;
            }
            
            this.saveToStorage();
        }
    }
    
    // Удаление товара из корзины
    removeItem(itemId) {
        this.items = this.items.filter(item => item.id !== itemId);
        this.saveToStorage();
    }
    
    // Очистка корзины
    clearCart() {
        this.items = [];
        this.saveToStorage();
    }
    
    // Получение общего количества товаров в корзине
    getTotalItems() {
        return this.items.reduce((total, item) => total + item.quantity, 0);
    }
    
    // Получение общей стоимости корзины
    getTotalPrice() {
        return this.items.reduce((total, item) => total + (item.price * item.quantity), 0);
    }
    
    // Обновление UI элементов, связанных с корзиной
    updateCartUI() {
        // Обновляем счетчик товаров в корзине
        const cartCountElem = document.getElementById('cart-count');
        if (cartCountElem) {
            const totalItems = this.getTotalItems();
            cartCountElem.textContent = totalItems;
            cartCountElem.style.display = totalItems > 0 ? 'inline-block' : 'none';
        }
        
        // Обновляем страницу корзины, если она открыта
        if (window.location.pathname === '/cart') {
            this.renderCartPage();
        }
    }
    
    // Отрисовка страницы корзины
    renderCartPage() {
        const cartContainer = document.getElementById('cart-items');
        const totalPriceElem = document.getElementById('cart-total-price');
        const checkoutBtn = document.getElementById('checkout-button');
        
        if (!cartContainer) return;
        
        // Очищаем контейнер
        cartContainer.innerHTML = '';
        
        if (this.items.length === 0) {
            cartContainer.innerHTML = `
                <div class="text-center py-5">
                    <h3>Ваша корзина пуста</h3>
                    <p>Добавьте блюда из меню, чтобы продолжить</p>
                    <a href="/menu" class="btn btn-primary mt-3">Перейти в меню</a>
                </div>
            `;
            
            if (totalPriceElem) totalPriceElem.textContent = '0 ₽';
            if (checkoutBtn) checkoutBtn.disabled = true;
            
            return;
        }
        
        // Отрисовываем каждый товар
        this.items.forEach(item => {
            const itemElem = document.createElement('div');
            itemElem.className = 'cart-item mb-4 p-3 border rounded';
            
            itemElem.innerHTML = `
                <div class="row align-items-center">
                    <div class="col-md-2">
                        <img src="${item.image || 'images/placeholder.jpg'}" alt="${item.name}" class="img-fluid rounded">
                    </div>
                    <div class="col-md-4">
                        <h5>${item.name}</h5>
                        <p class="text-muted">${item.price} ₽ за шт.</p>
                    </div>
                    <div class="col-md-3">
                        <div class="input-group">
                            <button class="btn btn-outline-secondary decrease-quantity" data-id="${item.id}">-</button>
                            <input type="number" class="form-control text-center quantity-input" value="${item.quantity}" min="1" data-id="${item.id}">
                            <button class="btn btn-outline-secondary increase-quantity" data-id="${item.id}">+</button>
                        </div>
                    </div>
                    <div class="col-md-2 text-end">
                        <p class="fw-bold">${item.price * item.quantity} ₽</p>
                    </div>
                    <div class="col-md-1 text-end">
                        <button class="btn btn-sm btn-outline-danger remove-item" data-id="${item.id}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            `;
            
            cartContainer.appendChild(itemElem);
        });
        
        // Добавляем обработчики событий для кнопок
        this.setupCartEventListeners();
        
        // Обновляем общую стоимость
        if (totalPriceElem) {
            totalPriceElem.textContent = `${this.getTotalPrice()} ₽`;
        }
        
        // Активируем кнопку оформления заказа
        if (checkoutBtn) {
            checkoutBtn.disabled = false;
        }
    }
    
    // Настройка обработчиков событий для страницы корзины
    setupCartEventListeners() {
        // Увеличение количества
        document.querySelectorAll('.increase-quantity').forEach(button => {
            button.addEventListener('click', () => {
                const itemId = parseInt(button.getAttribute('data-id'));
                const item = this.items.find(i => i.id === itemId);
                if (item) {
                    this.updateItemQuantity(itemId, item.quantity + 1);
                }
            });
        });
        
        // Уменьшение количества
        document.querySelectorAll('.decrease-quantity').forEach(button => {
            button.addEventListener('click', () => {
                const itemId = parseInt(button.getAttribute('data-id'));
                const item = this.items.find(i => i.id === itemId);
                if (item && item.quantity > 1) {
                    this.updateItemQuantity(itemId, item.quantity - 1);
                } else if (item) {
                    this.removeItem(itemId);
                }
            });
        });
        
        // Изменение значения в поле ввода
        document.querySelectorAll('.quantity-input').forEach(input => {
            input.addEventListener('change', () => {
                const itemId = parseInt(input.getAttribute('data-id'));
                const newQuantity = parseInt(input.value);
                if (newQuantity > 0) {
                    this.updateItemQuantity(itemId, newQuantity);
                } else {
                    input.value = 1;
                    this.updateItemQuantity(itemId, 1);
                }
            });
        });
        
        // Удаление товара
        document.querySelectorAll('.remove-item').forEach(button => {
            button.addEventListener('click', () => {
                const itemId = parseInt(button.getAttribute('data-id'));
                this.removeItem(itemId);
            });
        });
        
        // Кнопка очистки корзины
        const clearButton = document.getElementById('clear-cart');
        if (clearButton) {
            clearButton.addEventListener('click', () => {
                if (confirm('Вы уверены, что хотите очистить корзину?')) {
                    this.clearCart();
                }
            });
        }
    }
    
    // Получение данных корзины для оформления заказа
    getOrderData() {
        return {
            items: this.items,
            totalPrice: this.getTotalPrice(),
            totalItems: this.getTotalItems()
        };
    }
}

// Глобальный экземпляр корзины
const cart = new Cart();

// Функция для добавления товара в корзину
function addToCart(itemId, name, price, image, quantity = 1) {
    cart.addItem({
        id: itemId,
        name: name,
        price: price,
        image: image
    }, quantity);
    
    // Показываем сообщение о добавлении товара
    showToast(`${name} добавлен в корзину`);
}

// Функция для отображения всплывающего сообщения
function showToast(message) {
    const toastContainer = document.getElementById('toast-container');
    
    if (!toastContainer) {
        // Создаем контейнер для уведомлений, если его нет
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    const toastId = `toast-${Date.now()}`;
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <strong class="me-auto">Корзина</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    document.getElementById('toast-container').innerHTML += toastHtml;
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Автоматически удаляем уведомление после закрытия
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Добавляем обработчики для кнопок "Добавить в корзину"
function setupAddToCartButtons() {
    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', () => {
            const itemId = parseInt(button.getAttribute('data-id'));
            const name = button.getAttribute('data-name');
            const price = parseFloat(button.getAttribute('data-price'));
            const image = button.getAttribute('data-image');
            
            addToCart(itemId, name, price, image);
        });
    });
}

// Инициализация после загрузки страницы
document.addEventListener('DOMContentLoaded', function() {
    cart.updateCartUI();
    setupAddToCartButtons();
    
    // Если мы на странице корзины, отрисовываем ее
    if (window.location.pathname === '/cart') {
        cart.renderCartPage();
    }
}); 