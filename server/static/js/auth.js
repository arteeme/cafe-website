// Аутентификация и управление пользователями

// Проверка авторизации пользователя
function isAuthenticated() {
    return localStorage.getItem('token') !== null;
}

// Получение токена
function getToken() {
    return localStorage.getItem('token');
}

// Получение информации о пользователе
function getCurrentUser() {
    const userData = localStorage.getItem('user');
    return userData ? JSON.parse(userData) : null;
}

// Установка заголовков авторизации для fetch запросов
function getAuthHeaders() {
    const token = getToken();
    return {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
    };
}

// Регистрация пользователя
async function registerUser(userData) {
    try {
        console.log('Начало регистрации пользователя:', userData.email);
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        // Добавляем проверку статуса HTTP-ответа
        if (!response.ok) {
            console.error('Ошибка HTTP при регистрации:', response.status);
            const errorData = await response.json();
            console.error('Детали ошибки:', errorData);
            return {
                success: false,
                message: errorData.message || `Ошибка HTTP ${response.status}`,
                error: errorData.error
            };
        }
        
        const data = await response.json();
        console.log('Результат регистрации:', data);
        
        if (data.success) {
            console.log('Регистрация успешна, сохраняем данные в localStorage');
            // Сохраняем токен и данные пользователя
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            updateAuthUI();
            
            // Перенаправляем на главную страницу
            console.log('Перенаправляем на главную страницу...');
            window.location.href = '/';
        }
        
        return data;
    } catch (error) {
        console.error('Ошибка при регистрации:', error);
        return {
            success: false,
            message: 'Ошибка сети при регистрации',
            error: error.toString()
        };
    }
}

// Вход пользователя
async function loginUser(credentials) {
    try {
        console.log('Начало входа пользователя:', credentials.email);
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(credentials)
        });
        
        // Добавляем проверку статуса HTTP-ответа
        if (!response.ok) {
            console.error('Ошибка HTTP при входе:', response.status);
            const errorData = await response.json();
            console.error('Детали ошибки:', errorData);
            return {
                success: false,
                message: errorData.message || `Ошибка HTTP ${response.status}`,
                error: errorData.error
            };
        }
        
        const data = await response.json();
        console.log('Результат входа:', data);
        
        if (data.success) {
            console.log('Вход успешен, сохраняем данные в localStorage');
            // Сохраняем токен и данные пользователя
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            updateAuthUI();
            
            // Перенаправляем на главную страницу
            console.log('Перенаправляем на главную страницу...');
            window.location.href = '/';
        }
        
        return data;
    } catch (error) {
        console.error('Ошибка при входе:', error);
        return {
            success: false,
            message: 'Ошибка сети при входе',
            error: error.toString()
        };
    }
}

// Выход пользователя
function logoutUser() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    updateAuthUI();
    // Если пользователь не на главной странице, перенаправляем его
    if (window.location.pathname !== '/') {
        window.location.href = '/';
    }
}

// Восстановление пароля
async function forgotPassword(email) {
    try {
        const response = await fetch('/api/auth/forgot-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        });
        
        return await response.json();
    } catch (error) {
        console.error('Ошибка при восстановлении пароля:', error);
        return {
            success: false,
            message: 'Ошибка сети при восстановлении пароля'
        };
    }
}

// Сброс пароля
async function resetPassword(resetData) {
    try {
        const response = await fetch('/api/auth/reset-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(resetData)
        });
        
        return await response.json();
    } catch (error) {
        console.error('Ошибка при сбросе пароля:', error);
        return {
            success: false,
            message: 'Ошибка сети при сбросе пароля'
        };
    }
}

// Обновление профиля пользователя
async function updateUserProfile(userData) {
    try {
        const response = await fetch('/api/auth/me', {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Обновляем данные пользователя в localStorage
            localStorage.setItem('user', JSON.stringify(data.user));
        }
        
        return data;
    } catch (error) {
        console.error('Ошибка при обновлении профиля:', error);
        return {
            success: false,
            message: 'Ошибка сети при обновлении профиля'
        };
    }
}

// Получение данных пользователя с сервера
async function fetchUserData() {
    if (!isAuthenticated()) return null;
    
    try {
        const response = await fetch('/api/auth/me', {
            headers: getAuthHeaders()
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Обновляем данные пользователя в localStorage
            localStorage.setItem('user', JSON.stringify(data.user));
            return data.user;
        } else {
            // Если токен недействителен, выходим
            logoutUser();
            return null;
        }
    } catch (error) {
        console.error('Ошибка при получении данных пользователя:', error);
        return null;
    }
}

// Обновление UI в зависимости от состояния авторизации
function updateAuthUI() {
    const isLoggedIn = isAuthenticated();
    const authLinks = document.getElementById('auth-links');
    const userDropdown = document.getElementById('user-dropdown');
    
    if (!authLinks || !userDropdown) return;
    
    if (isLoggedIn) {
        // Пользователь вошел в систему
        authLinks.style.display = 'none';
        userDropdown.style.display = 'block';
        
        const user = getCurrentUser();
        const userNameElement = document.getElementById('user-name');
        if (userNameElement && user) {
            userNameElement.textContent = user.name;
        }
    } else {
        // Пользователь не авторизован
        authLinks.style.display = 'block';
        userDropdown.style.display = 'none';
    }
}

// Настройка форм аутентификации
function setupAuthForms() {
    // Форма регистрации
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const nameInput = registerForm.querySelector('#register-name');
            const emailInput = registerForm.querySelector('#register-email');
            const passwordInput = registerForm.querySelector('#register-password');
            const confirmInput = registerForm.querySelector('#register-confirm');
            
            // Валидация формы
            if (passwordInput.value !== confirmInput.value) {
                showError('Пароли не совпадают');
                return;
            }
            
            // Проверка длины пароля
            if (passwordInput.value.length < 6) {
                showError('Пароль должен содержать минимум 6 символов');
                return;
            }
            
            const userData = {
                name: nameInput.value,
                email: emailInput.value,
                password: passwordInput.value
            };
            
            const submitButton = registerForm.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.textContent = 'Регистрация...';
            
            try {
                const result = await registerUser(userData);
                if (result.success) {
                    showSuccess('Регистрация успешна!');
                    // Перенаправление уже происходит в функции registerUser
                } else {
                    const errorMessage = result.message || 'Ошибка при регистрации. Попробуйте еще раз.';
                    const errorDetails = result.error ? `\nДетали: ${result.error}` : '';
                    console.error('Подробности ошибки регистрации:', result);
                    showError(errorMessage);
                }
            } catch (error) {
                console.error('Исключение при регистрации:', error);
                showError('Произошла непредвиденная ошибка при регистрации. Попробуйте позже.');
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }
        });
    }
    
    // Форма входа
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const emailInput = loginForm.querySelector('#login-email');
            const passwordInput = loginForm.querySelector('#login-password');
            
            const credentials = {
                email: emailInput.value,
                password: passwordInput.value
            };
            
            const submitButton = loginForm.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.textContent = 'Вход...';
            
            try {
                const result = await loginUser(credentials);
                if (result.success) {
                    showSuccess('Вход выполнен успешно!');
                    // Перенаправление уже происходит в функции loginUser
                } else {
                    const errorMessage = result.message || 'Неверный email или пароль.';
                    console.error('Подробности ошибки входа:', result);
                    showError(errorMessage);
                }
            } catch (error) {
                console.error('Исключение при входе:', error);
                showError('Произошла непредвиденная ошибка при входе. Попробуйте позже.');
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }
        });
    }
    
    // Форма восстановления пароля
    const forgotForm = document.getElementById('forgot-password-form');
    if (forgotForm) {
        forgotForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const emailInput = forgotForm.querySelector('#forgot-email');
            
            const submitButton = forgotForm.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.textContent = 'Отправка...';
            
            try {
                const result = await forgotPassword(emailInput.value);
                if (result.success) {
                    showSuccess('Инструкции по восстановлению пароля отправлены на ваш email.');
                    // Закрываем модальное окно
                    const modal = bootstrap.Modal.getInstance(document.getElementById('forgotPasswordModal'));
                    if (modal) modal.hide();
                } else {
                    showError(result.message || 'Не удалось отправить инструкции. Проверьте email.');
                }
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }
        });
    }
    
    // Кнопка выхода
    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', (e) => {
            e.preventDefault();
            logoutUser();
        });
    }
}

// Инициализация после загрузки страницы
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем актуальность данных пользователя
    if (isAuthenticated()) {
        fetchUserData();
    }
    
    updateAuthUI();
    setupAuthForms();
}); 