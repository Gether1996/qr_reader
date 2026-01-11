// Company Register Password Toggle Functionality

function initCompanyRegisterPasswordToggle() {
    const togglePassword = document.querySelector('#togglePassword');
    const password = document.querySelector('#password');
    const toggleConfirmPassword = document.querySelector('#toggleConfirmPassword');
    const confirmPassword = document.querySelector('#confirm_password');

    if (togglePassword && password) {
        togglePassword.addEventListener('click', function () {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    }

    if (toggleConfirmPassword && confirmPassword) {
        toggleConfirmPassword.addEventListener('click', function () {
            const type = confirmPassword.getAttribute('type') === 'password' ? 'text' : 'password';
            confirmPassword.setAttribute('type', type);
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    }
}

// Validation for required fields
function initFormValidation() {
    const form = document.getElementById('company-register-form');
    if (!form) return;
    
    const requiredFields = ['name', 'email', 'password', 'confirm_password'];
    
    form.addEventListener('submit', function(e) {
        let isValid = true;
        
        requiredFields.forEach(fieldName => {
            const field = document.getElementById(fieldName);
            if (field && !field.value.trim()) {
                field.classList.add('is-invalid');
                field.style.borderColor = '#dc3545';
                isValid = false;
            } else if (field) {
                field.classList.remove('is-invalid');
                field.style.borderColor = '';
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            return false;
        }
    });
    
    // Remove red border on input
    requiredFields.forEach(fieldName => {
        const field = document.getElementById(fieldName);
        if (field) {
            field.addEventListener('input', function() {
                if (this.value.trim()) {
                    this.classList.remove('is-invalid');
                    this.style.borderColor = '';
                }
            });
        }
    });
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        initCompanyRegisterPasswordToggle();
        initFormValidation();
    });
} else {
    initCompanyRegisterPasswordToggle();
    initFormValidation();
}
