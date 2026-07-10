/**
 * Task Management System - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {

    // ========================================
    // Auto-dismiss flash messages after 4s
    // ========================================
    const flashMessages = document.getElementById('flash-messages');
    if (flashMessages) {
        setTimeout(function () {
            flashMessages.style.transition = 'opacity 0.5s ease';
            flashMessages.style.opacity = '0';
            setTimeout(function () {
                if (flashMessages.parentNode) {
                    flashMessages.remove();
                }
            }, 500);
        }, 4000);
    }

    // ========================================
    // Login form loading state
    // ========================================
    const loginForm = document.querySelector('.login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function () {
            const btn = document.getElementById('login-btn');
            if (btn) {
                btn.disabled = true;
                const btnText = btn.querySelector('.btn-text');
                const btnLoader = btn.querySelector('.btn-loader');
                if (btnText) btnText.style.display = 'none';
                if (btnLoader) btnLoader.style.display = 'inline-flex';
            }
        });
    }

    // ========================================
    // Form validation - employee & task forms
    // ========================================
    const appForms = document.querySelectorAll('.app-form');
    appForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const requiredFields = form.querySelectorAll('[required]');
            let valid = true;

            requiredFields.forEach(function (field) {
                if (!field.value.trim()) {
                    field.style.borderColor = '#ef4444';
                    field.style.boxShadow = '0 0 0 3px rgba(239,68,68,0.1)';
                    valid = false;
                } else {
                    field.style.borderColor = '';
                    field.style.boxShadow = '';
                }
            });

            if (!valid) {
                e.preventDefault();
                showToast('Please fill in all required fields.', 'error');
            }
        });
    });

    // ========================================
    // Status & Completed sync on task form
    // ========================================
    const statusSelect = document.getElementById('status');
    const completedSelect = document.getElementById('completed');

    if (statusSelect && completedSelect) {
        statusSelect.addEventListener('change', function () {
            if (this.value === 'Completed') {
                completedSelect.value = 'True';
            }
        });

        completedSelect.addEventListener('change', function () {
            if (this.value === 'True') {
                statusSelect.value = 'Completed';
            } else if (statusSelect.value === 'Completed') {
                statusSelect.value = 'Pending';
            }
        });
    }

    // ========================================
    // Remove error styling on input focus
    // ========================================
    document.addEventListener('focusin', function (e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') {
            e.target.style.borderColor = '';
            e.target.style.boxShadow = '';
        }
    });

});

// ========================================
// Delete Confirmation Modal
// ========================================
function confirmDelete(itemName, deleteUrl) {
    const modal = document.getElementById('confirm-modal');
    const message = document.getElementById('confirm-message');
    const form = document.getElementById('confirm-form');

    message.textContent = 'Are you sure you want to delete "' + itemName + '"? This action cannot be undone.';
    form.action = deleteUrl;
    modal.style.display = 'flex';
}

function closeModal() {
    const modal = document.getElementById('confirm-modal');
    modal.style.display = 'none';
}

// Close modal on overlay click
document.addEventListener('click', function (e) {
    if (e.target.id === 'confirm-modal') {
        closeModal();
    }
});

// Close modal on Escape key
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// ========================================
// Toast Notification
// ========================================
function showToast(message, type) {
    type = type || 'success';

    var existing = document.querySelector('.toast');
    if (existing) existing.remove();

    var toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(function () {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.5s ease';
        setTimeout(function () {
            if (toast.parentNode) toast.remove();
        }, 500);
    }, 3000);
}
