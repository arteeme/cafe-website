// Управление профилем пользователя

// Загрузка данных пользователя
async function loadUserProfile() {
    if (!isAuthenticated()) {
        window.location.href = '/login?redirect=profile';
        return;
    }
    
    try {
        const userData = await fetchUserData();
        if (userData) {
            fillProfileForm(userData);
        }
    } catch (error) {
        console.error('Ошибка при загрузке профиля:', error);
    }
}

// Заполнение формы профиля данными
function fillProfileForm(userData) {
    // Заполняем основную информацию
    const nameInput = document.getElementById('profile-name');
    const emailInput = document.getElementById('profile-email');
    const phoneInput = document.getElementById('profile-phone');
    const birthdateInput = document.getElementById('profile-birthdate');
    
    if (nameInput) nameInput.value = userData.name || '';
    if (emailInput) emailInput.value = userData.email || '';
    if (phoneInput) phoneInput.value = userData.phone || '';
    if (birthdateInput) birthdateInput.value = userData.birthdate || '';
}

// Обработка формы обновления профиля
async function updateProfile(profileData) {
    try {
        const response = await fetch('/api/auth/me', {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(profileData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Обновляем данные пользователя в localStorage
            localStorage.setItem('user_data', JSON.stringify(data.user));
            
            // Обновляем отображение имени в шапке
            updateAuthUI();
            return { success: true };
        } else {
            return { 
                success: false, 
                message: data.message || 'Ошибка обновления профиля.'
            };
        }
    } catch (error) {
        console.error('Ошибка при обновлении профиля:', error);
        return {
            success: false,
            message: 'Ошибка сети. Проверьте подключение к интернету.'
        };
    }
}

// Обработка формы смены пароля
async function changePassword(passwordData) {
    try {
        const response = await fetch('/api/auth/change-password', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(passwordData)
        });
        
        return await response.json();
    } catch (error) {
        console.error('Ошибка при смене пароля:', error);
        return {
            success: false,
            message: 'Ошибка сети. Проверьте подключение к интернету.'
        };
    }
}

// Загрузка избранных товаров
async function loadFavorites() {
    if (!isAuthenticated()) return;
    
    try {
        const response = await fetch('/api/favorites', {
            headers: getAuthHeaders()
        });
        
        const data = await response.json();
        
        if (data.success) {
            renderFavorites(data.favorites);
        } else {
            const favoritesContainer = document.getElementById('favorites-list');
            if (favoritesContainer) {
                favoritesContainer.innerHTML = `
                    <div class="alert alert-danger">
                        ${data.message || 'Не удалось загрузить избранные товары. Попробуйте позже.'}
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Ошибка при загрузке избранных товаров:', error);
    }
}

// Отображение избранных товаров
function renderFavorites(favorites) {
    const favoritesContainer = document.getElementById('favorites-list');
    if (!favoritesContainer) return;
    
    if (!favorites || favorites.length === 0) {
        favoritesContainer.innerHTML = `
            <div class="text-center py-4">
                <h4>У вас пока нет избранных блюд</h4>
                <p>Добавляйте блюда в избранное, чтобы быстро находить их при следующих заказах</p>
                <a href="/menu" class="btn btn-primary mt-2">Перейти в меню</a>
            </div>
        `;
        return;
    }
    
    favoritesContainer.innerHTML = '';
    
    // Создаем сетку для отображения избранных блюд
    const row = document.createElement('div');
    row.className = 'row';
    
    favorites.forEach(item => {
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-4';
        
        col.innerHTML = `
            <div class="card h-100">
                <img src="${item.image || 'images/placeholder.jpg'}" class="card-img-top" alt="${item.name}">
                <div class="card-body">
                    <h5 class="card-title">${item.name}</h5>
                    <p class="card-text">${item.description}</p>
                    <p class="fw-bold">${item.price} ₽</p>
                    <div class="d-flex justify-content-between">
                        <button class="btn btn-primary add-to-cart-btn" 
                            data-id="${item.id}" 
                            data-name="${item.name}" 
                            data-price="${item.price}" 
                            data-image="${item.image || 'images/placeholder.jpg'}">
                            В корзину
                        </button>
                        <button class="btn btn-outline-danger remove-favorite" data-id="${item.id}">
                            <i class="bi bi-heart-fill"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        row.appendChild(col);
    });
    
    favoritesContainer.appendChild(row);
    
    // Добавляем обработчики событий для кнопок
    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', () => {
            const itemId = parseInt(button.getAttribute('data-id'));
            const name = button.getAttribute('data-name');
            const price = parseFloat(button.getAttribute('data-price'));
            const image = button.getAttribute('data-image');
            
            addToCart(itemId, name, price, image);
        });
    });
    
    document.querySelectorAll('.remove-favorite').forEach(button => {
        button.addEventListener('click', async () => {
            const itemId = parseInt(button.getAttribute('data-id'));
            
            try {
                const response = await fetch(`/api/favorites/${itemId}`, {
                    method: 'DELETE',
                    headers: getAuthHeaders()
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Удаляем элемент из DOM
                    button.closest('.col-md-4').remove();
                    
                    // Если больше нет избранных товаров, показываем сообщение
                    if (document.querySelectorAll('.col-md-4').length === 0) {
                        loadFavorites();
                    }
                } else {
                    alert(data.message || 'Ошибка при удалении из избранного. Попробуйте позже.');
                }
            } catch (error) {
                console.error('Ошибка при удалении из избранного:', error);
                alert('Произошла ошибка. Попробуйте позже.');
            }
        });
    });
}

// Загрузка адресов доставки
async function loadAddresses() {
    if (!isAuthenticated()) return;
    
    try {
        const response = await fetch('/api/addresses', {
            headers: getAuthHeaders()
        });
        
        const data = await response.json();
        
        if (data.success) {
            renderAddresses(data.addresses);
        } else {
            const addressesContainer = document.getElementById('addresses-list');
            if (addressesContainer) {
                addressesContainer.innerHTML = `
                    <div class="alert alert-danger">
                        ${data.message || 'Не удалось загрузить адреса доставки. Попробуйте позже.'}
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Ошибка при загрузке адресов доставки:', error);
    }
}

// Отображение адресов доставки
function renderAddresses(addresses) {
    const addressesContainer = document.getElementById('addresses-list');
    if (!addressesContainer) return;
    
    if (!addresses || addresses.length === 0) {
        addressesContainer.innerHTML = `
            <div class="text-center py-4">
                <h4>У вас пока нет сохраненных адресов</h4>
                <p>Добавьте адрес доставки для быстрого оформления заказа</p>
                <button class="btn btn-primary mt-2" data-bs-toggle="modal" data-bs-target="#addAddressModal">Добавить адрес</button>
            </div>
        `;
        return;
    }
    
    addressesContainer.innerHTML = '';
    
    addresses.forEach(address => {
        const addressItem = document.createElement('div');
        addressItem.className = 'card mb-3';
        
        addressItem.innerHTML = `
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h5 class="card-title">${address.title}</h5>
                        <p class="card-text">
                            ${address.street}, ${address.city}
                            ${address.postal ? `, ${address.postal}` : ''}
                        </p>
                        ${address.notes ? `<p class="card-text text-muted small">${address.notes}</p>` : ''}
                    </div>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-outline-secondary edit-address" data-id="${address.id}">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger delete-address" data-id="${address.id}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        addressesContainer.appendChild(addressItem);
    });
    
    // Добавляем обработчики событий для кнопок
    document.querySelectorAll('.edit-address').forEach(button => {
        button.addEventListener('click', () => {
            const addressId = button.getAttribute('data-id');
            // Здесь будет логика для редактирования адреса
            alert('Редактирование адреса будет доступно в будущих обновлениях');
        });
    });
    
    document.querySelectorAll('.delete-address').forEach(button => {
        button.addEventListener('click', async () => {
            if (!confirm('Вы уверены, что хотите удалить этот адрес?')) return;
            
            const addressId = button.getAttribute('data-id');
            
            try {
                const response = await fetch(`/api/addresses/${addressId}`, {
                    method: 'DELETE',
                    headers: getAuthHeaders()
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Удаляем элемент из DOM
                    button.closest('.card').remove();
                    
                    // Если больше нет адресов, показываем сообщение
                    if (document.querySelectorAll('.edit-address').length === 0) {
                        loadAddresses();
                    }
                } else {
                    alert(data.message || 'Ошибка при удалении адреса. Попробуйте позже.');
                }
            } catch (error) {
                console.error('Ошибка при удалении адреса:', error);
                alert('Произошла ошибка. Попробуйте позже.');
            }
        });
    });
}

// Настройка обработчиков форм
function setupForms() {
    // Форма обновления профиля
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const nameInput = this.querySelector('#profile-name');
            const phoneInput = this.querySelector('#profile-phone');
            const birthdateInput = this.querySelector('#profile-birthdate');
            
            const profileData = {
                name: nameInput.value.trim(),
                phone: phoneInput.value.trim(),
                birthdate: birthdateInput.value || null
            };
            
            const submitButton = this.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.textContent = 'Сохранение...';
            
            try {
                const result = await updateProfile(profileData);
                
                if (result.success) {
                    alert('Профиль успешно обновлен!');
                } else {
                    alert(result.message || 'Ошибка обновления профиля. Попробуйте позже.');
                }
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }
        });
    }
    
    // Форма смены пароля
    const passwordForm = document.getElementById('password-form');
    if (passwordForm) {
        passwordForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const currentPasswordInput = this.querySelector('#current-password');
            const newPasswordInput = this.querySelector('#new-password');
            const confirmPasswordInput = this.querySelector('#confirm-password');
            
            // Проверка совпадения паролей
            if (newPasswordInput.value !== confirmPasswordInput.value) {
                alert('Новый пароль и подтверждение не совпадают');
                return;
            }
            
            const passwordData = {
                currentPassword: currentPasswordInput.value,
                newPassword: newPasswordInput.value
            };
            
            const submitButton = this.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.textContent = 'Изменение...';
            
            try {
                const result = await changePassword(passwordData);
                
                if (result.success) {
                    alert('Пароль успешно изменен!');
                    this.reset();
                } else {
                    alert(result.message || 'Ошибка смены пароля. Попробуйте позже.');
                }
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }
        });
    }
    
    // Форма добавления адреса
    const saveAddressBtn = document.getElementById('save-address-btn');
    if (saveAddressBtn) {
        saveAddressBtn.addEventListener('click', async function() {
            const titleInput = document.getElementById('address-title');
            const streetInput = document.getElementById('address-street');
            const cityInput = document.getElementById('address-city');
            const postalInput = document.getElementById('address-postal');
            const notesInput = document.getElementById('address-notes');
            
            // Проверка обязательных полей
            if (!titleInput.value.trim() || !streetInput.value.trim() || !cityInput.value.trim()) {
                alert('Пожалуйста, заполните все обязательные поля');
                return;
            }
            
            const addressData = {
                title: titleInput.value.trim(),
                street: streetInput.value.trim(),
                city: cityInput.value.trim(),
                postal: postalInput.value.trim(),
                notes: notesInput.value.trim()
            };
            
            const originalText = saveAddressBtn.textContent;
            saveAddressBtn.disabled = true;
            saveAddressBtn.textContent = 'Сохранение...';
            
            try {
                const response = await fetch('/api/addresses', {
                    method: 'POST',
                    headers: getAuthHeaders(),
                    body: JSON.stringify(addressData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert('Адрес успешно добавлен!');
                    
                    // Закрываем модальное окно
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addAddressModal'));
                    modal.hide();
                    
                    // Очищаем форму
                    document.getElementById('address-form').reset();
                    
                    // Перезагружаем список адресов
                    loadAddresses();
                } else {
                    alert(data.message || 'Ошибка добавления адреса. Попробуйте позже.');
                }
            } catch (error) {
                console.error('Ошибка при добавлении адреса:', error);
                alert('Произошла ошибка. Попробуйте позже.');
            } finally {
                saveAddressBtn.disabled = false;
                saveAddressBtn.textContent = originalText;
            }
        });
    }
}

// Обработчики для переключения вкладок
function setupTabLinks() {
    const tabLinks = document.querySelectorAll('.list-group-item');
    
    if (tabLinks.length === 0) return;
    
    tabLinks.forEach(link => {
        link.addEventListener('click', function() {
            const tabId = this.getAttribute('data-bs-target');
            
            // Загружаем данные для выбранной вкладки
            switch (tabId) {
                case '#orders-tab':
                    // Загрузка истории заказов через order.js
                    if (typeof initOrderHistoryPage === 'function') {
                        initOrderHistoryPage();
                    }
                    break;
                case '#favorites-tab':
                    loadFavorites();
                    break;
                case '#addresses-tab':
                    loadAddresses();
                    break;
            }
        });
    });
}

// Инициализация страницы профиля
function initProfilePage() {
    // Проверяем авторизацию
    if (!isAuthenticated()) {
        window.location.href = '/login?redirect=profile';
        return;
    }
    
    loadUserProfile();
    setupForms();
    setupTabLinks();
    
    // Загружаем данные для активной вкладки
    const activeTab = document.querySelector('.tab-pane.active');
    if (activeTab) {
        const tabId = activeTab.id;
        
        switch (tabId) {
            case 'orders-tab':
                // Загрузка истории заказов через order.js
                if (typeof initOrderHistoryPage === 'function') {
                    initOrderHistoryPage();
                }
                break;
            case 'favorites-tab':
                loadFavorites();
                break;
            case 'addresses-tab':
                loadAddresses();
                break;
        }
    }
}

// Инициализация после загрузки страницы
document.addEventListener('DOMContentLoaded', function() {
    // Инициализируем профиль только на соответствующей странице
    if (window.location.pathname === '/profile') {
        initProfilePage();
    }
}); 