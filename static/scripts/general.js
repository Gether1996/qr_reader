/**
 * General utility functions for QR Reader System
 */

// SweetAlert2 consistent styling
const swalConfig = {
    confirmButtonColor: '#2563eb',
    cancelButtonColor: '#6b7280',
    confirmButtonText: translations?.confirmDeactivate || 'Yes, deactivate!',
    cancelButtonText: translations?.cancel || 'Cancel'
};

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
            confirmButtonColor: swalConfig.confirmButtonColor
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
            confirmButtonColor: swalConfig.confirmButtonColor
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
            confirmButtonColor: swalConfig.confirmButtonColor
        });
    }
}

/**
 * Show a confirmation dialog using SweetAlert2
 * @param {string} title - Confirmation title
 * @param {string} text - Confirmation text
 * @param {Function} onConfirm - Callback function when confirmed
 */
function showConfirm(title, text, onConfirm) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'warning',
            title: title,
            text: text,
            showCancelButton: true,
            confirmButtonColor: '#ef4444',
            cancelButtonColor: swalConfig.cancelButtonColor,
            confirmButtonText: swalConfig.confirmButtonText,
            cancelButtonText: swalConfig.cancelButtonText
        }).then((result) => {
            if (result.isConfirmed && typeof onConfirm === 'function') {
                onConfirm();
            }
        });
    }
}

/**
 * Global delete confirmation function
 * @param {string} itemName - Name of the item to delete
 * @param {string} itemType - Type of item (e.g., 'User', 'QR')
 * @returns {Promise} SweetAlert2 promise
 */
function confirmDelete(itemName, itemType) {
    const titleKey = `delete${itemType}Title`;
    const textKey = `delete${itemType}Text`;
    
    return Swal.fire({
        title: translations[titleKey] || 'Deactivate?',
        text: (translations[textKey] || 'Are you sure you want to deactivate {name}?').replace('{name}', itemName),
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444',
        cancelButtonColor: '#6b7280',
        confirmButtonText: translations.confirmDeactivate || 'Yes, deactivate!',
        cancelButtonText: translations.cancel || 'Cancel',
        reverseButtons: true
    });
}
