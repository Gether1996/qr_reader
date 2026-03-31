// Company Settings JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeSettingsPage();
});

function initializeSettingsPage() {
    const form = document.getElementById('company-settings-form');
    const cancelBtn = document.getElementById('cancel-settings');
    const resetPasswordBtn = document.getElementById('reset-password-btn');

    // Store original form values
    const originalValues = new FormData(form);

    // Cancel button - reset form to original values
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            if (hasFormChanged(form, originalValues)) {
                appUI.fire({
                    title: translations.confirmCancel || 'Cancel Changes?',
                    text: translations.confirmCancelText || 'All unsaved changes will be lost.',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: translations.yes || 'Yes, cancel',
                    cancelButtonText: translations.no || 'No, continue editing',
                    confirmButtonColor: '#d33',
                    cancelButtonColor: '#3085d6'
                }).then((result) => {
                    if (result.isConfirmed) {
                        form.reset();
                        // Restore original values
                        for (let [key, value] of originalValues.entries()) {
                            const field = form.elements[key];
                            if (field) {
                                if (field.type === 'checkbox') {
                                    field.checked = value === 'on';
                                } else {
                                    field.value = value;
                                }
                            }
                        }
                    }
                });
            }
        });
    }

    // Form submission
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            saveSettings();
        });
    }

    // Reset password button
    if (resetPasswordBtn) {
        resetPasswordBtn.addEventListener('click', function() {
            requestPasswordReset();
        });
    }
}
function hasFormChanged(form, originalValues) {
    const currentValues = new FormData(form);
    
    for (let [key, value] of originalValues.entries()) {
        const currentValue = currentValues.get(key) || '';
        if (value !== currentValue) {
            return true;
        }
    }
    
    return false;
}

function saveSettings() {
    const form = document.getElementById('company-settings-form');
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Validate required fields
    const companyName = document.getElementById('company_name');
    if (!companyName.value.trim()) {
        companyName.style.borderColor = '#dc3545';
        companyName.focus();
        appUI.fire({
            title: translations.error || 'Error!',
            text: translations.companyNameRequired || 'Company name is required',
            icon: 'error',
            confirmButtonText: translations.ok || 'OK'
        });
        return;
    } else {
        companyName.style.borderColor = '';
    }
    
    // Disable submit button
    submitButton.disabled = true;
    const originalText = submitButton.innerHTML;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ' + (translations.saving || 'Saving...');

    fetch(window.location.href, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            appUI.fire({
                title: translations.success || 'Success!',
                text: data.message || translations.settingsSaved || 'Settings have been saved successfully.',
                icon: 'success',
                confirmButtonText: 'OK',
                confirmButtonColor: '#10b981'
            }).then(() => {
                // Reload page to show updated values
                window.location.reload();
            });
        } else {
            appUI.fire({
                title: translations.error || 'Error',
                text: data.message || translations.saveFailed || 'Failed to save settings. Please try again.',
                icon: 'error',
                confirmButtonText: 'OK',
                confirmButtonColor: '#ef4444'
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        appUI.fire({
            title: translations.error || 'Error',
            text: translations.networkError || 'Network error. Please check your connection and try again.',
            icon: 'error',
            confirmButtonText: 'OK',
            confirmButtonColor: '#ef4444'
        });
    })
    .finally(() => {
        // Re-enable submit button
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
    });
}

function requestPasswordReset() {
    appUI.fire({
        title: translations.resetPassword || 'Reset Password',
        html: translations.resetPasswordText || 'A password reset link will be sent to your email address.<br><br>Do you want to continue?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: translations.sendResetLink || 'Send Reset Link',
        cancelButtonText: translations.cancel || 'Cancel',
        confirmButtonColor: '#667eea',
        cancelButtonColor: '#6b7280'
    }).then((result) => {
        if (result.isConfirmed) {
            // Show loading state
            appUI.fire({
                title: translations.sending || 'Sending...',
                text: translations.pleaseWait || 'Please wait while we send the reset link.',
                icon: 'info',
                allowOutsideClick: false,
                allowEscapeKey: false,
                showConfirmButton: false,
                willOpen: () => {
                    appUI.showLoading();
                }
            });

            // Send request
            fetch('/company/request-password-reset/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    appUI.fire({
                        title: translations.emailSent || 'Email Sent!',
                        html: data.message || translations.emailSentText || 'A password reset link has been sent to your email address.<br><br>Please check your inbox and follow the instructions.',
                        icon: 'success',
                        confirmButtonText: 'OK',
                        confirmButtonColor: '#10b981'
                    });
                } else {
                    appUI.fire({
                        title: translations.error || 'Error',
                        text: data.message || translations.sendFailed || 'Failed to send reset email. Please try again.',
                        icon: 'error',
                        confirmButtonText: 'OK',
                        confirmButtonColor: '#ef4444'
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                appUI.fire({
                    title: translations.error || 'Error',
                    text: translations.networkError || 'Network error. Please check your connection and try again.',
                    icon: 'error',
                    confirmButtonText: 'OK',
                    confirmButtonColor: '#ef4444'
                });
            });
        }
    });
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Form validation
function validateForm(form) {
    const companyName = form.elements['company_name'];
    
    if (!companyName || !companyName.value.trim()) {
        appUI.fire({
            title: translations.validationError || 'Validation Error',
            text: translations.companyNameRequired || 'Company name is required.',
            icon: 'warning',
            confirmButtonText: 'OK',
            confirmButtonColor: '#f59e0b'
        });
        companyName.focus();
        return false;
    }
    
    return true;
}