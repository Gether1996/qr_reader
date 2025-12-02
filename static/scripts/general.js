/**
 * General utility functions for QR Reader System
 */

/**
 * Get CSRF token from cookies for Django POST requests
 * @param {string} name - Cookie name (usually 'csrftoken')
 * @returns {string|null} Cookie value or null if not found
 */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Show a success message using SweetAlert2
 * @param {string} title - Message title
 * @param {string} text - Message text
 */
function showSuccess(title, text) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'success',
            title: title,
            text: text,
            confirmButtonColor: '#2563eb'
        });
    }
}

/**
 * Show an error message using SweetAlert2
 * @param {string} title - Message title
 * @param {string} text - Message text
 */
function showError(title, text) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'error',
            title: title,
            text: text,
            confirmButtonColor: '#2563eb'
        });
    }
}

/**
 * Show a warning message using SweetAlert2
 * @param {string} title - Message title
 * @param {string} text - Message text
 */
function showWarning(title, text) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'warning',
            title: title,
            text: text,
            confirmButtonColor: '#2563eb'
        });
    }
}
