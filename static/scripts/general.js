/**
 * General utility functions for QR Reader System
 */

// SweetAlert2 consistent styling with gradients
const swalConfig = {
    customClass: {
        confirmButton: 'swal-btn-gradient-blue',
        cancelButton: 'swal-btn-gradient-gray',
        popup: 'swal-popup-rounded'
    },
    buttonsStyling: false,
    confirmButtonText: translations?.confirmDeactivate || 'Yes, deactivate!',
    cancelButtonText: translations?.cancel || 'Cancel',
    showClass: {
        popup: 'animate__animated animate__fadeIn animate__faster'
    },
    hideClass: {
        popup: 'animate__animated animate__fadeOut animate__faster'
    }
};

// Add custom styles to document
if (!document.getElementById('swal-custom-styles')) {
    const style = document.createElement('style');
    style.id = 'swal-custom-styles';
    style.textContent = `
        .swal-popup-rounded {
            border-radius: 16px !important;
            padding: 2rem !important;
            max-width: 95vw !important;
            width: auto !important;
        }
        .swal2-html-container .form-control,
        .swal2-html-container .form-select {
            border-radius: 8px !important;
            border: 2px solid #e5e7eb !important;
            transition: all 0.3s ease !important;
        }
        .swal2-html-container .form-control:focus,
        .swal2-html-container .form-select:focus {
            border-color: #2563eb !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
            outline: none !important;
        }
        .swal2-html-container .form-label {
            color: #374151 !important;
            margin-bottom: 0.5rem !important;
        }
        .swal2-popup {
            overflow-x: hidden !important;
            overflow-y: auto !important;
        }
        .swal2-html-container {
            overflow-x: hidden !important;
            overflow-y: visible !important;
            max-width: 100% !important;
        }
        .swal2-input, .swal2-select, .swal2-textarea {
            max-width: 100% !important;
            box-sizing: border-box !important;
        }
        .swal-btn-gradient-blue {
            background: linear-gradient(135deg, #2563eb, #1e40af) !important;
            color: white !important;
            border: none !important;
            padding: 0.75rem 2rem !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
        }
        .swal-btn-gradient-blue:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4) !important;
        }
        .swal-btn-gradient-gray {
            background: linear-gradient(135deg, #6b7280, #4b5563) !important;
            color: white !important;
            border: none !important;
            padding: 0.75rem 2rem !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3) !important;
        }
        .swal-btn-gradient-gray:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 16px rgba(107, 114, 128, 0.4) !important;
        }
        .swal-btn-gradient-red {
            background: linear-gradient(135deg, #ef4444, #dc2626) !important;
            color: white !important;
            border: none !important;
            padding: 0.75rem 2rem !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3) !important;
        }
        .swal-btn-gradient-red:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4) !important;
        }
        .swal-btn-gradient-green {
            background: linear-gradient(135deg, #10b981, #059669) !important;
            color: white !important;
            border: none !important;
            padding: 0.75rem 2rem !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
        }
        .swal-btn-gradient-green:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4) !important;
        }
        .swal2-title {
            font-weight: 700 !important;
            font-size: 1.75rem !important;
        }
        .swal2-html-container {
            font-size: 1rem !important;
            color: #4b5563 !important;
        }
        .swal-toast-rounded {
            border-radius: 12px !important;
            font-weight: 600 !important;
        }
        .swal2-toast .swal2-icon {
            margin: 0 0.5rem 0 0 !important;
        }
    `;
    document.head.appendChild(style);
}

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
            customClass: {
                confirmButton: 'swal-btn-gradient-green',
                popup: 'swal-popup-rounded'
            },
            buttonsStyling: false,
            showClass: swalConfig.showClass,
            hideClass: swalConfig.hideClass
        });
    }
}

/**
 * Show an error message using SweetAlert2
 * @param {string} title - Message title (not used in toast mode)
 * @param {string} text - Message text
 */
function showError(title, text) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'error',
            text: text,
            timer: 2000,
            showConfirmButton: false,
            position: 'top-end',
            toast: true,
            background: 'linear-gradient(135deg, #ef4444, #dc2626)',
            color: 'white',
            customClass: {
                popup: 'swal-toast-rounded'
            },
            showClass: {
                popup: 'animate__animated animate__fadeInRight animate__faster'
            },
            hideClass: {
                popup: 'animate__animated animate__fadeOutRight animate__faster'
            }
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
            customClass: {
                confirmButton: 'swal-btn-gradient-blue',
                popup: 'swal-popup-rounded'
            },
            buttonsStyling: false,
            showClass: swalConfig.showClass,
            hideClass: swalConfig.hideClass
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
            customClass: {
                confirmButton: 'swal-btn-gradient-red',
                cancelButton: 'swal-btn-gradient-gray',
                popup: 'swal-popup-rounded'
            },
            buttonsStyling: false,
            confirmButtonText: swalConfig.confirmButtonText,
            cancelButtonText: swalConfig.cancelButtonText,
            reverseButtons: true,
            showClass: swalConfig.showClass,
            hideClass: swalConfig.hideClass
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
        customClass: {
            confirmButton: 'swal-btn-gradient-red',
            cancelButton: 'swal-btn-gradient-gray',
            popup: 'swal-popup-rounded'
        },
        buttonsStyling: false,
        confirmButtonText: translations.confirmDeactivate || 'Yes, deactivate!',
        cancelButtonText: translations.cancel || 'Cancel',
        reverseButtons: true,
        showClass: swalConfig.showClass,
        hideClass: swalConfig.hideClass
    });
}
