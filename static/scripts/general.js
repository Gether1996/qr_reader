/**
 * General utility functions for QR Reader System
 */

/**
 * Get CSRF token from cookies for Django POST requests
 * @param {string} name - Cookie name (usually 'csrftoken')
 * @returns {string|null} Cookie value or null if not found
 */

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
