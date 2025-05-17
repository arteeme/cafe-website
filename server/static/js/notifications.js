/**
 * Utilities for displaying user notifications
 */

// Create toast container if it doesn't exist
function ensureToastContainer() {
    if (!document.querySelector('.toast-container')) {
        const toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = 9999;
        document.body.appendChild(toastContainer);
    }
}

// Show notification
function showNotification(message, type = 'info', duration = 5000) {
    ensureToastContainer();
    const container = document.querySelector('.toast-container');
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast bg-${type} text-white`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    // Set toast content
    toast.innerHTML = `
        <div class="toast-header bg-${type} text-white">
            <strong class="me-auto">${getTypeTitle(type)}</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    // Add toast to container
    container.appendChild(toast);
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: duration
    });
    
    bsToast.show();
    
    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
    
    return bsToast;
}

// Helper function to get title based on notification type
function getTypeTitle(type) {
    switch (type) {
        case 'success':
            return 'Успех';
        case 'danger':
            return 'Ошибка';
        case 'warning':
            return 'Внимание';
        case 'info':
        default:
            return 'Информация';
    }
}

// Success notification
function showSuccess(message, duration = 5000) {
    return showNotification(message, 'success', duration);
}

// Error notification
function showError(message, duration = 5000) {
    return showNotification(message, 'danger', duration);
}

// Warning notification
function showWarning(message, duration = 5000) {
    return showNotification(message, 'warning', duration);
}

// Info notification
function showInfo(message, duration = 5000) {
    return showNotification(message, 'info', duration);
}

// Confirm dialog using Bootstrap modal
function showConfirm(title, message, confirmCallback, cancelCallback = null) {
    // Create modal if it doesn't exist
    if (!document.getElementById('confirmModal')) {
        const modalHtml = `
            <div class="modal fade" id="confirmModal" tabindex="-1" aria-labelledby="confirmModalLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="confirmModalLabel">Подтверждение</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            Вы уверены?
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" id="confirmModalCancel">Отмена</button>
                            <button type="button" class="btn btn-primary" id="confirmModalConfirm">Подтвердить</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = modalHtml;
        document.body.appendChild(modalContainer.firstChild);
    }
    
    const modal = document.getElementById('confirmModal');
    const modalTitle = modal.querySelector('.modal-title');
    const modalBody = modal.querySelector('.modal-body');
    const confirmButton = document.getElementById('confirmModalConfirm');
    const cancelButton = document.getElementById('confirmModalCancel');
    
    // Update content
    modalTitle.textContent = title;
    modalBody.textContent = message;
    
    // Initialize Bootstrap modal
    const bsModal = new bootstrap.Modal(modal);
    
    // Setup event handlers
    const confirmHandler = function() {
        confirmButton.removeEventListener('click', confirmHandler);
        cancelButton.removeEventListener('click', cancelHandler);
        bsModal.hide();
        if (typeof confirmCallback === 'function') {
            confirmCallback();
        }
    };
    
    const cancelHandler = function() {
        confirmButton.removeEventListener('click', confirmHandler);
        cancelButton.removeEventListener('click', cancelHandler);
        if (typeof cancelCallback === 'function') {
            cancelCallback();
        }
    };
    
    // Attach events
    confirmButton.addEventListener('click', confirmHandler);
    cancelButton.addEventListener('click', cancelHandler);
    
    // Show modal
    bsModal.show();
    
    // Return modal instance for further manipulation if needed
    return bsModal;
} 