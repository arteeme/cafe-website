// Управление заказами

// Рассчет стоимости доставки
function calculateDeliveryFee(address, subtotal) {
    // Пример простой логики расчета стоимости доставки
    // В реальном приложении это может быть сложнее (на основе расстояния, веса и т.д.)
    if (subtotal >= 1500) {
        return 0; // Бесплатная доставка при заказе от 1500₽
    }
    
    return 300; // Базовая стоимость доставки
}

// Применение промокода
async function applyPromoCode(code, subtotal) {
    try {
        const response = await fetch(`/api/promo/check?code=${encodeURIComponent(code)}&subtotal=${subtotal}`);
        const data = await response.json();
        
        return data;
    } catch (error) {
        console.error('Ошибка при проверке промокода:', error);
        return {
            success: false,
            message: 'Не удалось проверить промокод. Попробуйте позже.'
        };
    }
}

// Создание заказа
async function createOrder(orderData) {
    try {
        const response = await fetch('/api/orders', {
            method: 'POST',
            headers: getAuthHeaders(), // Используем getAuthHeaders из auth.js
            body: JSON.stringify(orderData)
        });
        
        return await response.json();
    } catch (error) {
        console.error('Ошибка при создании заказа:', error);
        return {
            success: false,
            message: 'Не удалось создать заказ. Проверьте соединение с интернетом.'
        };
    }
}

// Получение истории заказов
async function getOrderHistory() {
    if (!isAuthenticated()) return { success: false, message: 'Требуется авторизация' };
    
    try {
        const response = await fetch('/api/orders/history', {
            headers: getAuthHeaders()
        });
        
        return await response.json();
    } catch (error) {
        console.error('Ошибка при получении истории заказов:', error);
        return {
            success: false,
            message: 'Не удалось загрузить историю заказов.'
        };
    }
}

// Повторение заказа
function repeatOrder(orderItems) {
    // Очищаем текущую корзину
    cart.clearCart();
    
    // Добавляем товары из предыдущего заказа
    orderItems.forEach(item => {
        cart.addItem({
            id: item.id,
            name: item.name,
            price: item.price,
            image: item.image
        }, item.quantity);
    });
    
    // Переходим на страницу корзины
    window.location.href = '/cart';
}

// Отображение истории заказов
function displayOrderHistory(orders) {
    const historyContainer = document.getElementById('order-history');
    if (!historyContainer) return;
    
    // Очищаем контейнер
    historyContainer.innerHTML = '';
    
    if (!orders || orders.length === 0) {
        historyContainer.innerHTML = `
            <div class="text-center py-4">
                <h4>У вас пока нет заказов</h4>
                <p>Перейдите в меню, чтобы сделать свой первый заказ</p>
                <a href="/menu" class="btn btn-primary mt-2">Перейти в меню</a>
            </div>
        `;
        return;
    }
    
    // Сортируем заказы по дате (новые вверху)
    orders.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    
    // Отрисовываем каждый заказ
    orders.forEach(order => {
        const orderDate = new Date(order.created_at);
        const formattedDate = orderDate.toLocaleDateString('ru-RU') + ' ' + orderDate.toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit'});
        
        const orderElem = document.createElement('div');
        orderElem.className = 'order-item card mb-4';
        
        orderElem.innerHTML = `
            <div class="card-header d-flex justify-content-between align-items-center">
                <div>
                    <h5 class="mb-0">Заказ #${order.order_number}</h5>
                    <small class="text-muted">${formattedDate}</small>
                </div>
                <span class="badge ${getBadgeClass(order.status)}">${order.status}</span>
            </div>
            <div class="card-body">
                <div class="order-items mb-3">
                    <h6>Состав заказа:</h6>
                    <ul class="list-group">
                        ${order.items.map(item => `
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                <span>${item.name}</span>
                                <span>${item.quantity} x ${item.price} ₽</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
                <div class="order-details">
                    <p><strong>Тип заказа:</strong> ${order.order_type}</p>
                    ${order.address ? `<p><strong>Адрес доставки:</strong> ${order.address}</p>` : ''}
                    <p><strong>Статус оплаты:</strong> ${order.payment_status}</p>
                    <p><strong>Способ оплаты:</strong> ${order.payment_method}</p>
                    ${order.comment ? `<p><strong>Комментарий:</strong> ${order.comment}</p>` : ''}
                    <div class="d-flex justify-content-between align-items-center mt-3">
                        <h5 class="mb-0">Итого: ${order.total_amount} ₽</h5>
                        <button class="btn btn-outline-primary repeat-order-btn" data-order='${JSON.stringify(order.items)}'>
                            Повторить заказ
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        historyContainer.appendChild(orderElem);
    });
    
    // Добавляем обработчики для кнопок "Повторить заказ"
    document.querySelectorAll('.repeat-order-btn').forEach(button => {
        button.addEventListener('click', () => {
            const orderItems = JSON.parse(button.getAttribute('data-order'));
            repeatOrder(orderItems);
        });
    });
}

// Определение класса для статуса заказа
function getBadgeClass(status) {
    switch (status) {
        case 'новый':
            return 'bg-primary';
        case 'подтвержден':
            return 'bg-info';
        case 'готовится':
            return 'bg-warning';
        case 'в пути':
            return 'bg-info';
        case 'доставлен':
            return 'bg-success';
        case 'отменен':
            return 'bg-danger';
        default:
            return 'bg-secondary';
    }
}

// Настройка формы оформления заказа
function setupCheckoutForm() {
    const checkoutForm = document.getElementById('checkout-form');
    if (!checkoutForm) return;
    
    // Получаем данные корзины
    const cartData = cart.getOrderData();
    
    // Если корзина пуста, перенаправляем на страницу корзины
    if (cartData.totalItems === 0) {
        window.location.href = '/cart';
        return;
    }
    
    // Отображаем краткую информацию о заказе
    const orderSummary = document.getElementById('order-summary');
    if (orderSummary) {
        orderSummary.innerHTML = `
            <h4 class="mb-3">Ваш заказ</h4>
            <p>Всего товаров: ${cartData.totalItems}</p>
            <p>Сумма заказа: ${cartData.totalPrice} ₽</p>
            <p id="delivery-fee">Доставка: <span>300 ₽</span></p>
            <p id="discount" style="display: none;">Скидка: <span>0 ₽</span></p>
            <h5>Итого: <span id="total-amount">${cartData.totalPrice + 300} ₽</span></h5>
        `;
    }
    
    // Обработчик для типа заказа (доставка/самовывоз)
    const orderTypeInputs = document.querySelectorAll('input[name="order_type"]');
    const deliveryAddressBlock = document.getElementById('delivery-address-block');
    
    orderTypeInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.value === 'доставка') {
                deliveryAddressBlock.style.display = 'block';
                
                // Рассчитываем стоимость доставки
                const deliveryFee = calculateDeliveryFee('', cartData.totalPrice);
                
                // Обновляем отображение
                updateOrderSummary(cartData.totalPrice, deliveryFee);
            } else {
                deliveryAddressBlock.style.display = 'none';
                
                // Убираем стоимость доставки
                updateOrderSummary(cartData.totalPrice, 0);
            }
        });
    });
    
    // Обработчик для промокода
    const promoForm = document.getElementById('promo-form');
    if (promoForm) {
        promoForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const promoCodeInput = this.querySelector('#promo-code');
            const promoCode = promoCodeInput.value.trim();
            
            if (!promoCode) return;
            
            const submitButton = this.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.textContent = 'Проверка...';
            
            try {
                const result = await applyPromoCode(promoCode, cartData.totalPrice);
                
                if (result.success) {
                    // Обновляем отображение
                    const deliveryFeeElem = document.getElementById('delivery-fee');
                    const deliveryFee = deliveryFeeElem ? parseInt(deliveryFeeElem.querySelector('span').textContent) : 0;
                    
                    // Показываем скидку
                    const discountElem = document.getElementById('discount');
                    if (discountElem) {
                        discountElem.style.display = 'block';
                        discountElem.querySelector('span').textContent = `${result.discount} ₽`;
                    }
                    
                    // Обновляем итоговую сумму
                    updateOrderSummary(cartData.totalPrice, deliveryFee, result.discount);
                    
                    // Сохраняем промокод для отправки
                    checkoutForm.setAttribute('data-promo', promoCode);
                    
                    // Сообщение об успехе
                    alert(`Промокод применен! Скидка: ${result.discount} ₽`);
                } else {
                    alert(result.message || 'Неверный промокод');
                    // Сбрасываем промокод
                    checkoutForm.removeAttribute('data-promo');
                }
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }
        });
    }
    
    // Обработчик отправки формы заказа
    checkoutForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Проверяем, что пользователь авторизован
        if (!isAuthenticated()) {
            alert('Для оформления заказа необходимо войти в аккаунт');
            window.location.href = '/login?redirect=checkout';
            return;
        }
        
        // Получаем тип заказа
        const orderType = document.querySelector('input[name="order_type"]:checked').value;
        
        // Проверяем адрес для доставки
        let address = '';
        if (orderType === 'доставка') {
            address = document.getElementById('address').value.trim();
            if (!address) {
                alert('Пожалуйста, укажите адрес доставки');
                return;
            }
        }
        
        // Получаем другие данные из формы
        const name = document.getElementById('name').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const comment = document.getElementById('comment').value.trim();
        const paymentMethod = document.querySelector('input[name="payment_method"]:checked').value;
        
        // Проверяем обязательные поля
        if (!name || !phone) {
            alert('Пожалуйста, заполните все обязательные поля');
            return;
        }
        
        // Формируем данные заказа
        const orderData = {
            items: cartData.items,
            total_amount: parseFloat(document.getElementById('total-amount').textContent),
            order_type: orderType,
            address: address,
            name: name,
            phone: phone,
            comment: comment,
            payment_method: paymentMethod,
            promo_code: checkoutForm.getAttribute('data-promo') || ''
        };
        
        const submitButton = checkoutForm.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = 'Оформление...';
        
        try {
            const result = await createOrder(orderData);
            
            if (result.success) {
                // Очищаем корзину
                cart.clearCart();
                
                // Показываем сообщение об успехе
                alert('Заказ успешно оформлен! Мы свяжемся с вами в ближайшее время.');
                
                // Перенаправляем на страницу с подтверждением
                window.location.href = `/order-confirmation?order_id=${result.order_id}`;
            } else {
                alert(result.message || 'Произошла ошибка при оформлении заказа');
            }
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    });
}

// Обновление сводки заказа
function updateOrderSummary(subtotal, deliveryFee, discount = 0) {
    const deliveryFeeElem = document.getElementById('delivery-fee');
    if (deliveryFeeElem) {
        deliveryFeeElem.querySelector('span').textContent = `${deliveryFee} ₽`;
    }
    
    const totalAmountElem = document.getElementById('total-amount');
    if (totalAmountElem) {
        totalAmountElem.textContent = `${subtotal + deliveryFee - discount} ₽`;
    }
}

// Инициализация страницы оформления заказа
function initCheckoutPage() {
    setupCheckoutForm();
}

// Инициализация страницы истории заказов
async function initOrderHistoryPage() {
    // Проверяем, что пользователь авторизован
    if (!isAuthenticated()) {
        window.location.href = '/login?redirect=profile';
        return;
    }
    
    const result = await getOrderHistory();
    
    if (result.success) {
        displayOrderHistory(result.orders);
    } else {
        const historyContainer = document.getElementById('order-history');
        if (historyContainer) {
            historyContainer.innerHTML = `
                <div class="alert alert-danger">
                    ${result.message || 'Не удалось загрузить историю заказов. Попробуйте позже.'}
                </div>
            `;
        }
    }
}

// Инициализация после загрузки страницы
document.addEventListener('DOMContentLoaded', function() {
    // Определяем текущую страницу
    const currentPath = window.location.pathname;
    
    if (currentPath === '/checkout') {
        initCheckoutPage();
    } else if (currentPath === '/profile' || currentPath === '/orders') {
        initOrderHistoryPage();
    }
}); 