// Company Dashboard JavaScript Functions

function createQRCode() {
    appUI.fire({
        title: translations.createQRCode,
        html: `
            <div class="swal-form-layout">
                <div class="swal-form-section">
                    <div class="swal-form-section-title">
                        <span class="swal-form-section-icon">
                            <i class="fas fa-qrcode"></i>
                        </span>
                        <span>${translations.createQRCode}</span>
                    </div>
                    <div class="swal-form-stack">
                        <div class="swal-form-field">
                            <label class="form-label swal-form-required" for="swal-qr-name">${translations.nameQr}</label>
                            <input type="text" id="swal-qr-name" class="form-control" placeholder="${translations.nameQr}" required autocomplete="off">
                        </div>
                        <div class="swal-form-field">
                            <label class="form-label swal-form-required" for="swal-qr-location">${translations.location}</label>
                            <input type="text" id="swal-qr-location" class="form-control" placeholder="${translations.location}" required autocomplete="off">
                        </div>
                    </div>
                </div>
                <div class="swal-form-section">
                    <div class="swal-form-section-title">
                        <span class="swal-form-section-icon">
                            <i class="fas fa-align-left"></i>
                        </span>
                        <span>${translations.additionalInfo}</span>
                    </div>
                    <div class="swal-form-field">
                        <textarea id="swal-qr-info" class="form-control" placeholder="${translations.additionalInfo}" rows="4"></textarea>
                    </div>
                </div>
            </div>
        `,
        width: '600px',
        showCancelButton: true,
        confirmButtonText: translations.create,
        cancelButtonText: translations.cancel,
        customClass: {
            confirmButton: 'swal-btn-gradient-green',
            cancelButton: 'swal-btn-gradient-gray',
            popup: 'swal-popup-rounded'
        },
        buttonsStyling: false,
        didOpen: () => {
            document.getElementById('swal-qr-name').focus();
        },
        preConfirm: () => {
            const name = document.getElementById('swal-qr-name').value.trim();
            const location = document.getElementById('swal-qr-location').value.trim();
            const additionalInfo = document.getElementById('swal-qr-info').value.trim();
            
            if (!name || !location) {
                appUI.showValidationMessage(translations.fillAllFields);
                return false;
            }

            return { name, location, additional_info: additionalInfo };
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const data = result.value;
            const langCode = window.location.pathname.split('/')[1];
            const createUrl = `/${langCode}/qr/create/`;

            // Show loading spinner
            appUI.fire({
                title: translations.pleaseWait || 'Please wait...',
                html: translations.creatingQRCode || 'Creating QR code...',
                allowOutsideClick: false,
                allowEscapeKey: false,
                didOpen: () => {
                    appUI.showLoading();
                }
            });

            fetch(createUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    appUI.fire({
                        icon: 'success',
                        title: translations.success,
                        text: translations.qrCodeCreated,
                        customClass: {
                            confirmButton: 'swal-btn-gradient-green',
                            popup: 'swal-popup-rounded'
                        },
                        buttonsStyling: false
                    }).then(() => {
                        location.reload();
                    });
                } else {
                    appUI.fire({
                        icon: 'error',
                        title: translations.error,
                        text: data.message || translations.qrCodeCreateFailed,
                        customClass: {
                            confirmButton: 'swal-btn-gradient-red',
                            popup: 'swal-popup-rounded'
                        },
                        buttonsStyling: false
                    });
                }
            })
            .catch(error => {
                appUI.fire({
                    icon: 'error',
                    title: translations.error,
                    text: translations.qrCodeCreateFailed,
                    customClass: {
                        confirmButton: 'swal-btn-gradient-red',
                        popup: 'swal-popup-rounded'
                    },
                    buttonsStyling: false
                });
            });
        }
    });
}
function createUser() {
    appUI.fire({
        title: translations.registerEmployee,
        html: `
            <div class="container-fluid px-0">
                <!-- Basic Information -->
                <div class="swal-section">
                    <div class="swal-section-title">
                        <i class="fas fa-user"></i>${translations.basicInfo || 'Basic Information'}
                    </div>
                    <div class="row g-2">
                        <div class="col-12">
                            <input type="text" id="swal-user-name" class="form-control required-field" placeholder="${translations.name} *" required autocomplete="off">
                        </div>
                        <div class="col-12">
                            <input type="email" id="swal-user-email" class="form-control required-field" placeholder="${translations.email} *" required autocomplete="off">
                        </div>
                        <div class="col-md-6 col-12">
                            <input type="text" id="swal-user-rc" class="form-control" placeholder="${translations.rc || 'Personal ID'}" autocomplete="off">
                        </div>
                        <div class="col-md-6 col-12">
                            <input type="tel" id="swal-user-phone" class="form-control" placeholder="${translations.phone || 'Phone'}" autocomplete="off">
                        </div>
                        <div class="col-12">
                            <label class="form-label mb-1 small">${translations.birthDate || 'Birth Date'}</label>
                            <input type="date" id="swal-user-birth-date" class="form-control">
                        </div>
                    </div>
                </div>

                <!-- Security -->
                <div class="swal-section">
                    <div class="swal-section-title">
                        <i class="fas fa-lock"></i>${translations.security || 'Security'} <span class="swal-optional-note">(${translations.optional || 'optional'})</span>
                    </div>
                    <div class="row g-2">
                        <div class="col-md-6 col-12">
                            <input type="password" id="swal-user-password" class="form-control" placeholder="${translations.passwordOptionalInvite || translations.password}" autocomplete="new-password">
                        </div>
                        <div class="col-md-6 col-12">
                            <input type="password" id="swal-user-password-confirm" class="form-control" placeholder="${translations.confirmPasswordOptional || translations.confirmPassword}" autocomplete="new-password">
                        </div>
                        <div class="col-12">
                            <div class="swal-helper-note">
                                <i class="fas fa-envelope me-1"></i>${translations.employeeInviteHint || 'Leave both password fields empty to send the employee an email with a password setup link valid for 24 hours.'}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Work Settings -->
                <div class="swal-section">
                    <div class="swal-section-title">
                        <i class="fas fa-briefcase"></i>${translations.workSettings || 'Work Settings'}
                    </div>
                    <div class="row g-2">
                        <div class="col-sm-6 col-12">
                            <label class="form-label mb-1 small required-field">${translations.basicWorkHours}</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-clock"></i></span>
                                <input type="number" id="swal-user-work-hours" class="form-control" value="160" required min="0" step="1">
                                <span class="input-group-text">h</span>
                            </div>
                        </div>
                        <div class="col-sm-6 col-12">
                            <label class="form-label mb-1 small required-field">${translations.holidaysPerYear}</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-umbrella-beach"></i></span>
                                <input type="number" id="swal-user-holidays" class="form-control required-field" value="20" required min="0" step="1">
                                <span class="input-group-text">days</span>
                            </div>
                        </div>
                        <div class="col-12 mt-3">
                            <label class="form-label mb-2 small">${translations.lunchBreakDuration || 'Lunch Break Duration'}</label>
                            <label class="swal-checkbox-label mb-2">
                                <input class="form-check-input" type="checkbox" id="swal-user-has-lunch-break" checked>
                                <span><i class="fas fa-utensils text-success me-1"></i>${translations.hasLunchBreak || 'Lunch Break'}</span>
                            </label>
                            <div class="input-group" id="lunch-break-duration-container">
                                <span class="input-group-text"><i class="fas fa-hourglass-half"></i></span>
                                <input type="number" id="swal-user-lunch-break" class="form-control required-field" value="30" required min="0" step="1">
                                <span class="input-group-text">min</span>
                            </div>
                            <div class="swal-helper-note">
                                <i class="fas fa-info-circle me-1"></i>${translations.lunchBreakInfo || 'Used only if employee does not scan a break QR code and if Automatic Lunch Breaks are enabled in company settings.'}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Role & Permissions -->
                <div class="swal-section">
                    <div class="swal-section-title">
                        <i class="fas fa-user-shield"></i>${translations.rolePermissions || 'Role & Permissions'}
                    </div>
                    <select id="swal-user-role" class="form-select mb-3">
                        <option value="employee">${translations.employee}</option>
                        <option value="manager">${translations.manager}</option>
                    </select>
                    
                    <div id="manager-permissions" style="display: none;">
                        <div class="d-flex flex-column gap-2 mb-3">
                            <label class="swal-checkbox-label">
                                <input class="form-check-input" type="checkbox" id="perm-edit-employees" checked>
                                <span><i class="fas fa-users text-primary me-1"></i>${translations.canEditEmployees}</span>
                            </label>
                            <label class="swal-checkbox-label">
                                <input class="form-check-input" type="checkbox" id="perm-edit-qr" checked>
                                <span><i class="fas fa-qrcode text-success me-1"></i>${translations.canEditQR}</span>
                            </label>
                            <label class="swal-checkbox-label">
                                <input class="form-check-input" type="checkbox" id="perm-edit-absences" checked>
                                <span><i class="fas fa-calendar-times text-warning me-1"></i>${translations.canEditAbsences}</span>
                            </label>
                        </div>
                        
                        <label class="swal-checkbox-label mb-3">
                            <input class="form-check-input" type="checkbox" id="manager-enable-notifications" checked>
                                <span><i class="fas fa-bell text-info me-1"></i>${translations.enableNotifications}</span>
                            </label>
                        
                        <div id="manager-notification-options" class="ps-3">
                            <div class="d-flex flex-column gap-2">
                                <label class="swal-inline-check-option">
                                    <input class="form-check-input" type="checkbox" id="manager-notify-arrival" checked>
                                    <span><i class="fas fa-sign-in-alt me-1"></i>${translations.arrival}</span>
                                </label>
                                <label class="swal-inline-check-option">
                                    <input class="form-check-input" type="checkbox" id="manager-notify-departure" checked>
                                    <span><i class="fas fa-sign-out-alt me-1"></i>${translations.departure}</span>
                                </label>
                                <label class="swal-inline-check-option">
                                    <input class="form-check-input" type="checkbox" id="manager-notify-vacation" checked>
                                    <span><i class="fas fa-calendar-times me-1"></i>${translations.vacation || 'Vacation/Absence'}</span>
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `,
        width: '760px',
        didOpen: () => {
            const hasLunchBreakCheckbox = document.getElementById('swal-user-has-lunch-break');
            const lunchBreakContainer = document.getElementById('lunch-break-duration-container');
            
            // Toggle lunch break duration field
            hasLunchBreakCheckbox.addEventListener('change', () => {
                lunchBreakContainer.style.display = hasLunchBreakCheckbox.checked ? 'flex' : 'none';
            });
            
            const roleSelect = document.getElementById('swal-user-role');
            const permissionsDiv = document.getElementById('manager-permissions');
            
            roleSelect.addEventListener('change', function() {
                if (this.value === 'manager') {
                    permissionsDiv.style.display = 'block';
                } else {
                    permissionsDiv.style.display = 'none';
                }
            });
            
            // Toggle notification options visibility
            const enableNotificationsCheckbox = document.getElementById('manager-enable-notifications');
            const notificationOptions = document.getElementById('manager-notification-options');
            
            if (enableNotificationsCheckbox) {
                enableNotificationsCheckbox.addEventListener('change', function() {
                    notificationOptions.style.display = this.checked ? 'block' : 'none';
                });
            }
        },
        showCancelButton: true,
        confirmButtonText: translations.register,
        cancelButtonText: translations.cancel,
        buttonsStyling: false,
        preConfirm: () => {
            // Remove previous error styling
            document.querySelectorAll('.field-error').forEach(el => el.classList.remove('field-error'));
            
            const name = document.getElementById('swal-user-name').value;
            const email = document.getElementById('swal-user-email').value;
            const rc = document.getElementById('swal-user-rc').value || null;
            const phone = document.getElementById('swal-user-phone').value || null;
            const birthDate = document.getElementById('swal-user-birth-date').value || null;
            const password = document.getElementById('swal-user-password').value;
            const passwordConfirm = document.getElementById('swal-user-password-confirm').value;
            const role = document.getElementById('swal-user-role').value;
            const workHours = document.getElementById('swal-user-work-hours').value;
            const holidays = document.getElementById('swal-user-holidays').value;
            const hasLunchBreak = document.getElementById('swal-user-has-lunch-break').checked;
            const lunchBreak = hasLunchBreak ? document.getElementById('swal-user-lunch-break').value : '0';
            
            // Validate required fields and add error styling
            const requiredFields = [
                { id: 'swal-user-name', value: name },
                { id: 'swal-user-email', value: email },
                { id: 'swal-user-work-hours', value: workHours },
                { id: 'swal-user-holidays', value: holidays }
            ];
            
            if (hasLunchBreak) {
                requiredFields.push({ id: 'swal-user-lunch-break', value: lunchBreak });
            }
            
            const emptyFields = requiredFields.filter(field => !field.value);
            if (emptyFields.length > 0) {
                emptyFields.forEach(field => {
                    document.getElementById(field.id).classList.add('field-error');
                });
                appUI.showValidationMessage(translations.fillAllFields);
                return false;
            }
            
            if ((password && !passwordConfirm) || (!password && passwordConfirm)) {
                document.getElementById('swal-user-password').classList.add('field-error');
                document.getElementById('swal-user-password-confirm').classList.add('field-error');
                appUI.showValidationMessage(translations.passwordBothOrInvite);
                return false;
            }

            if (password && password.length < 10) {
                document.getElementById('swal-user-password').classList.add('field-error');
                appUI.showValidationMessage(translations.passwordMinLengthStrong || translations.passwordMinLength);
                return false;
            }

            if (password && !/[A-Z]/.test(password)) {
                document.getElementById('swal-user-password').classList.add('field-error');
                appUI.showValidationMessage(translations.passwordUppercaseRequired);
                return false;
            }

            if (password && password !== passwordConfirm) {
                document.getElementById('swal-user-password').classList.add('field-error');
                document.getElementById('swal-user-password-confirm').classList.add('field-error');
                appUI.showValidationMessage(translations.passwordsDontMatch);
                return false;
            }

            const data = { 
                name, 
                email, 
                rc, 
                phone, 
                birth_date: birthDate,
                basic_work_hours: parseInt(workHours), 
                holidays_per_year: parseInt(holidays), 
                lunch_break_duration: parseInt(lunchBreak), 
                is_manager: role === 'manager' 
            };

            if (password) {
                data.password = password;
                data.password_confirm = passwordConfirm;
            }
            
            if (role === 'manager') {
                data.can_edit_employees = document.getElementById('perm-edit-employees').checked;
                data.can_edit_qr_codes = document.getElementById('perm-edit-qr').checked;
                data.can_edit_absences = document.getElementById('perm-edit-absences').checked;
                
                // Notification preferences
                const enableNotifications = document.getElementById('manager-enable-notifications')?.checked || false;
                data.notify_arrival = enableNotifications && (document.getElementById('manager-notify-arrival')?.checked || false);
                data.notify_departure = enableNotifications && (document.getElementById('manager-notify-departure')?.checked || false);
                data.notify_vacation = enableNotifications && (document.getElementById('manager-notify-vacation')?.checked || false);
            }

            // First check if email exists
            const langCode = window.location.pathname.split('/')[1];
            const checkEmailUrl = `/${langCode}/user/check-email/`;
            
            return fetch(checkEmailUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ email: email })
            })
            .then(response => response.json())
            .then(result => {
                if (result.exists) {
                    appUI.showValidationMessage(result.message || translations.emailAlreadyExists || 'Email already exists');
                    return false;
                }
                
                // If email is available, submit the user creation
                appUI.fire({
                    title: translations.pleaseWait || 'Please wait...',
                    html: translations.registeringUser || 'Registering user...',
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    didOpen: () => {
                        appUI.showLoading();
                    }
                });
                
                const createUrl = `/${langCode}/user/create/`;
                return fetch(createUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        return data;
                    } else {
                        appUI.showValidationMessage(data.message || translations.userRegisterFailed);
                        return false;
                    }
                });
            })
            .catch(error => {
                appUI.showValidationMessage(error.message || translations.userRegisterFailed);
                return false;
            });
        }
    }).then((result) => {
        if (result.isConfirmed) {
            appUI.fire({
                icon: 'success',
                title: translations.success,
                text: (result.value && result.value.message) || translations.userRegistered,
                customClass: {
                    confirmButton: 'swal-btn-gradient-green',
                    popup: 'swal-popup-rounded'
                },
                buttonsStyling: false
            }).then(() => {
                location.reload();
            });
        }
    });
}

function editUser(userId, name, email, basicWorkHours, holidaysPerYear, hasLunchBreak, lunchBreakDuration, isManager, canEditEmployees, canEditQR, canEditAbsences, notifyArrival, notifyDeparture, notifyVacation, rc = '', phone = '', birthDate = '') {
    // Determine if notifications are enabled (any notification is checked)
    const notificationsEnabled = notifyArrival || notifyDeparture || notifyVacation;
    
    appUI.fire({
        title: translations.editEmployee,
        html: `
            <div class="container-fluid px-0">
                <!-- Basic Information -->
                <div class="swal-section">
                    <div class="swal-section-title">
                        <i class="fas fa-user"></i>${translations.basicInfo || 'Basic Information'}
                    </div>
                    <div class="row g-2">
                        <div class="col-12">
                            <input type="text" id="swal-edit-user-name" class="form-control" value="${name}" placeholder="${translations.name} *" required autocomplete="off">
                        </div>
                        <div class="col-12">
                            <input type="email" id="swal-edit-user-email" class="form-control" value="${email}" placeholder="${translations.email} *" required autocomplete="off">
                        </div>
                        <div class="col-md-6 col-12">
                            <input type="text" id="swal-edit-user-rc" class="form-control" value="${rc || ''}" placeholder="${translations.rc || 'Personal ID'}" autocomplete="off">
                        </div>
                        <div class="col-md-6 col-12">
                            <input type="tel" id="swal-edit-user-phone" class="form-control" value="${phone || ''}" placeholder="${translations.phone || 'Phone'}" autocomplete="off">
                        </div>
                        <div class="col-12">
                            <label class="form-label mb-1 small">${translations.birthDate || 'Birth Date'}</label>
                            <input type="date" id="swal-edit-user-birth-date" class="form-control" value="${birthDate || ''}">
                        </div>
                    </div>
                </div>

                <!-- Security -->
                <div class="swal-section">
                    <div class="swal-section-title">
                        <i class="fas fa-lock"></i>${translations.security || 'Security'} <span class="swal-optional-note">(${translations.optional || 'optional'})</span>
                    </div>
                    <div class="row g-2">
                        <div class="col-md-6 col-12">
                            <input type="password" id="swal-edit-user-password" class="form-control" placeholder="${translations.newPassword}" autocomplete="new-password">
                        </div>
                        <div class="col-md-6 col-12">
                            <input type="password" id="swal-edit-user-password-confirm" class="form-control" placeholder="${translations.confirmPassword}" autocomplete="new-password">
                        </div>
                    </div>
                </div>

                <!-- Work Settings -->
                <div class="swal-section">
                    <div class="swal-section-title">
                        <i class="fas fa-briefcase"></i>${translations.workSettings || 'Work Settings'}
                    </div>
                    <div class="row g-2">
                        <div class="col-sm-6 col-12">
                            <label class="form-label mb-1 small required-field">${translations.basicWorkHours}</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-clock"></i></span>
                                <input type="number" id="swal-edit-user-work-hours" class="form-control" value="${basicWorkHours || 160}" required min="0" step="1">
                                <span class="input-group-text">h</span>
                            </div>
                        </div>
                        <div class="col-sm-6 col-12">
                            <label class="form-label mb-1 small required-field">${translations.holidaysPerYear}</label>
                            <div class="input-group">
                                <span class="input-group-text"><i class="fas fa-umbrella-beach"></i></span>
                                <input type="number" id="swal-edit-user-holidays" class="form-control" value="${holidaysPerYear || 20}" required min="0" step="1">
                                <span class="input-group-text">days</span>
                            </div>
                        </div>
                        <div class="col-12 mt-3">
                            <label class="form-label mb-2 small">${translations.lunchBreakDuration || 'Lunch Break Duration'}</label>
                            <label class="swal-checkbox-label mb-2">
                                <input class="form-check-input" type="checkbox" id="swal-edit-user-has-lunch-break" ${hasLunchBreak ? 'checked' : ''}>
                                <span><i class="fas fa-utensils text-success me-1"></i>${translations.hasLunchBreak || 'Lunch Break'}</span>
                            </label>
                            <div class="input-group" id="edit-lunch-break-duration-container" style="display: ${hasLunchBreak ? 'flex' : 'none'};">
                                <span class="input-group-text"><i class="fas fa-hourglass-half"></i></span>
                                <input type="number" id="swal-edit-user-lunch-break" class="form-control" value="${lunchBreakDuration || 30}" required min="0" step="1">
                                <span class="input-group-text">min</span>
                            </div>
                            <div class="swal-helper-note">
                                <i class="fas fa-info-circle me-1"></i>${translations.lunchBreakInfo || 'Used only if employee does not scan a break QR code and if Automatic Lunch Breaks are enabled in company settings.'}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Role & Permissions -->
                <div class="swal-section">
                    <div class="swal-section-title">
                        <i class="fas fa-user-shield"></i>${translations.rolePermissions || 'Role & Permissions'}
                    </div>
                    <select id="swal-edit-user-role" class="form-select mb-3">
                        <option value="employee" ${!isManager ? 'selected' : ''}>${translations.employee}</option>
                        <option value="manager" ${isManager ? 'selected' : ''}>${translations.manager}</option>
                    </select>
                    
                    <div id="edit-manager-permissions" style="display: ${isManager ? 'block' : 'none'};">
                        <div class="d-flex flex-column gap-2 mb-3">
                            <label class="swal-checkbox-label">
                                <input class="form-check-input" type="checkbox" id="edit-perm-edit-employees" ${canEditEmployees ? 'checked' : ''}>
                                <span><i class="fas fa-users text-primary me-1"></i>${translations.canEditEmployees}</span>
                            </label>
                            <label class="swal-checkbox-label">
                                <input class="form-check-input" type="checkbox" id="edit-perm-edit-qr" ${canEditQR ? 'checked' : ''}>
                                <span><i class="fas fa-qrcode text-success me-1"></i>${translations.canEditQR}</span>
                            </label>
                            <label class="swal-checkbox-label">
                                <input class="form-check-input" type="checkbox" id="edit-perm-edit-absences" ${canEditAbsences ? 'checked' : ''}>
                                <span><i class="fas fa-calendar-times text-warning me-1"></i>${translations.canEditAbsences}</span>
                            </label>
                        </div>
                        
                        <label class="swal-checkbox-label mb-3">
                            <input class="form-check-input" type="checkbox" id="edit-manager-enable-notifications" ${notificationsEnabled ? 'checked' : ''}>
                                <span><i class="fas fa-bell text-info me-1"></i>${translations.enableNotifications}</span>
                            </label>
                        
                        <div id="edit-manager-notification-options" class="ps-3" style="display: ${notificationsEnabled ? 'block' : 'none'};">
                            <div class="d-flex flex-column gap-2">
                                <label class="swal-inline-check-option">
                                    <input class="form-check-input" type="checkbox" id="edit-manager-notify-arrival" ${notifyArrival ? 'checked' : ''}>
                                    <span><i class="fas fa-sign-in-alt me-1"></i>${translations.arrival}</span>
                                </label>
                                <label class="swal-inline-check-option">
                                    <input class="form-check-input" type="checkbox" id="edit-manager-notify-departure" ${notifyDeparture ? 'checked' : ''}>
                                    <span><i class="fas fa-sign-out-alt me-1"></i>${translations.departure}</span>
                                </label>
                                <label class="swal-inline-check-option">
                                    <input class="form-check-input" type="checkbox" id="edit-manager-notify-vacation" ${notifyVacation ? 'checked' : ''}>
                                    <span><i class="fas fa-calendar-times me-1"></i>${translations.vacation || 'Vacation/Absence'}</span>
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `,
        width: '760px',
        didOpen: () => {
            const hasLunchBreakCheckbox = document.getElementById('swal-edit-user-has-lunch-break');
            const lunchBreakContainer = document.getElementById('edit-lunch-break-duration-container');
            
            // Toggle lunch break duration field
            hasLunchBreakCheckbox.addEventListener('change', () => {
                lunchBreakContainer.style.display = hasLunchBreakCheckbox.checked ? 'flex' : 'none';
            });
            
            const roleSelect = document.getElementById('swal-edit-user-role');
            const permissionsDiv = document.getElementById('edit-manager-permissions');
            
            roleSelect.addEventListener('change', function() {
                if (this.value === 'manager') {
                    permissionsDiv.style.display = 'block';
                } else {
                    permissionsDiv.style.display = 'none';
                }
            });
            
            // Toggle notification options visibility
            const enableNotificationsCheckbox = document.getElementById('edit-manager-enable-notifications');
            const notificationOptions = document.getElementById('edit-manager-notification-options');
            
            if (enableNotificationsCheckbox) {
                enableNotificationsCheckbox.addEventListener('change', function() {
                    notificationOptions.style.display = this.checked ? 'block' : 'none';
                });
            }
        },
        showCancelButton: true,
        confirmButtonText: translations.save,
        cancelButtonText: translations.cancel,
        buttonsStyling: false,
        preConfirm: async () => {
            // Remove previous error styling
            document.querySelectorAll('.field-error').forEach(el => el.classList.remove('field-error'));
            
            const name = document.getElementById('swal-edit-user-name').value;
            const email = document.getElementById('swal-edit-user-email').value;
            const rc = document.getElementById('swal-edit-user-rc').value || null;
            const phone = document.getElementById('swal-edit-user-phone').value || null;
            const birthDate = document.getElementById('swal-edit-user-birth-date').value || null;
            const password = document.getElementById('swal-edit-user-password').value;
            const passwordConfirm = document.getElementById('swal-edit-user-password-confirm').value;
            const workHours = document.getElementById('swal-edit-user-work-hours').value;
            const holidays = document.getElementById('swal-edit-user-holidays').value;
            const hasLunchBreak = document.getElementById('swal-edit-user-has-lunch-break').checked;
            const lunchBreak = hasLunchBreak ? document.getElementById('swal-edit-user-lunch-break').value : 0;
            const role = document.getElementById('swal-edit-user-role').value;
            
            // Validate required fields and add error styling
            const requiredFields = [
                { id: 'swal-edit-user-name', value: name },
                { id: 'swal-edit-user-email', value: email },
                { id: 'swal-edit-user-work-hours', value: workHours },
                { id: 'swal-edit-user-holidays', value: holidays }
            ];
            
            if (hasLunchBreak) {
                requiredFields.push({ id: 'swal-edit-user-lunch-break', value: lunchBreak });
            }
            
            const emptyFields = requiredFields.filter(field => !field.value);
            if (emptyFields.length > 0) {
                emptyFields.forEach(field => {
                    document.getElementById(field.id).classList.add('field-error');
                });
                appUI.showValidationMessage(translations.fillAllFields);
                return false;
            }
            
            // Validate password only if provided
            if (password || passwordConfirm) {
                if (password.length < 8) {
                    document.getElementById('swal-edit-user-password').classList.add('field-error');
                    appUI.showValidationMessage(translations.passwordMinLength);
                    return false;
                }
                
                if (password !== passwordConfirm) {
                    document.getElementById('swal-edit-user-password').classList.add('field-error');
                    document.getElementById('swal-edit-user-password-confirm').classList.add('field-error');
                    appUI.showValidationMessage(translations.passwordsDontMatch);
                    return false;
                }
            }

            const data = { 
                name, 
                email, 
                rc, 
                phone, 
                birth_date: birthDate, 
                basic_work_hours: parseInt(workHours), 
                holidays_per_year: parseInt(holidays), 
                has_lunch_break: hasLunchBreak, 
                lunch_break_duration: parseInt(lunchBreak), 
                is_manager: role === 'manager' 
            };
            if (password) {
                data.password = password;
            }
            
            if (role === 'manager') {
                data.can_edit_employees = document.getElementById('edit-perm-edit-employees').checked;
                data.can_edit_qr_codes = document.getElementById('edit-perm-edit-qr').checked;
                data.can_edit_absences = document.getElementById('edit-perm-edit-absences').checked;
                
                // Notification preferences
                const enableNotifications = document.getElementById('edit-manager-enable-notifications')?.checked || false;
                data.notify_arrival = enableNotifications && (document.getElementById('edit-manager-notify-arrival')?.checked || false);
                data.notify_departure = enableNotifications && (document.getElementById('edit-manager-notify-departure')?.checked || false);
                data.notify_vacation = enableNotifications && (document.getElementById('edit-manager-notify-vacation')?.checked || false);
            }

            const langCode = window.location.pathname.split('/')[1];
            const editUrl = `/${langCode}/company/user/${userId}/edit/`;
            
            // Check if email changed
            const originalEmail = '${email}'.toLowerCase();
            const newEmail = email.toLowerCase();
            
            if (originalEmail !== newEmail) {
                // Email changed, check if new email exists
                const checkEmailUrl = `/${langCode}/user/check-email/`;
                
                return fetch(checkEmailUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ email: email })
                })
                .then(response => response.json())
                .then(result => {
                    if (result.exists) {
                        appUI.showValidationMessage(result.message || translations.emailAlreadyExists || 'Email already exists');
                        return false;
                    }
                    
                    // If email is available, submit the update
                    appUI.fire({
                        title: translations.pleaseWait || 'Please wait...',
                        html: translations.updatingUser || 'Updating user...',
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        didOpen: () => {
                            appUI.showLoading();
                        }
                    });
                    
                    return fetch(editUrl, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify(data)
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            return data;
                        } else {
                            appUI.showValidationMessage(data.message || translations.userUpdateFailed);
                            return false;
                        }
                    });
                })
                .catch(error => {
                    appUI.showValidationMessage(error.message || translations.userUpdateFailed);
                    return false;
                });
            } else {
                // Email not changed, just submit
                appUI.fire({
                    title: translations.pleaseWait || 'Please wait...',
                    html: translations.updatingUser || 'Updating user...',
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    didOpen: () => {
                        appUI.showLoading();
                    }
                });
                
                return fetch(editUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        return data;
                    } else {
                        appUI.showValidationMessage(data.message || translations.userUpdateFailed);
                        return false;
                    }
                })
                .catch(error => {
                    appUI.showValidationMessage(error.message || translations.userUpdateFailed);
                    return false;
                });
            }
        }
    }).then((result) => {
        if (result.isConfirmed) {
            appUI.fire({
                icon: 'success',
                title: translations.success,
                text: translations.userUpdated,
                customClass: {
                    confirmButton: 'swal-btn-gradient-green',
                    popup: 'swal-popup-rounded'
                },
                buttonsStyling: false
            }).then(() => {
                location.reload();
            });
        }
    });
}

function deleteUser(userId, userName) {
    console.log('deleteUser called:', userId, userName);
    confirmDelete(userName, 'User').then((result) => {
        console.log('Swal result:', result);
        if (result.isConfirmed) {
            const langCode = window.location.pathname.split('/')[1];
            const deleteUrl = `/${langCode}/company/user/${userId}/delete/`;
            console.log('Delete URL:', deleteUrl);
            console.log('CSRF Token:', csrfToken);
            
            // Show loading spinner
            appUI.fire({
                title: translations.pleaseWait || 'Please wait...',
                html: translations.deletingUser || 'Deleting user...',
                allowOutsideClick: false,
                allowEscapeKey: false,
                didOpen: () => {
                    appUI.showLoading();
                }
            });
            
            fetch(deleteUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showSuccess(translations.deleted, translations.userDeleted);
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showError(translations.error, data.message);
                }
            })
            .catch(error => {
                showError(translations.error, translations.userDeleteFailed);
            });
        }
    });
}

function deleteQRCode(qrId, qrName) {
    console.log('deleteQRCode called:', qrId, qrName);
    confirmDelete(qrName, 'QR').then((result) => {
        console.log('Swal result:', result);
        if (result.isConfirmed) {
            const langCode = window.location.pathname.split('/')[1];
            const deleteUrl = `/${langCode}/qr/delete/${qrId}/`;
            console.log('Delete URL:', deleteUrl);
            
            // Show loading spinner
            appUI.fire({
                title: translations.pleaseWait || 'Please wait...',
                html: translations.deletingQRCode || 'Deleting QR code...',
                allowOutsideClick: false,
                allowEscapeKey: false,
                didOpen: () => {
                    appUI.showLoading();
                }
            });
            
            fetch(deleteUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showSuccess(translations.deleted, translations.qrCodeDeleted);
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showError(translations.error, data.message);
                }
            })
            .catch(error => {
                showError(translations.error, translations.qrCodeDeleteFailed);
            });
        }
    });
}

function showQRPrintModal(qrCodeUrl, qrCodeName, qrCodeId) {
    const langCode = window.location.pathname.split('/')[1];
    const printUrl = `/${langCode}/qr/${qrCodeId}/pdf/`;
    
    appUI.fire({
        title: qrCodeName,
        html: `
            <div class="text-center">
                <img src="${qrCodeUrl}" alt="QR Code" style="width: 300px; height: 300px; margin: 20px auto; display: block;">
            </div>
        `,
        width: '500px',
        showCancelButton: true,
        confirmButtonText: '<i class="fas fa-print me-2"></i>' + translations.print,
        cancelButtonText: translations.close,
        customClass: {
            confirmButton: 'swal-btn-gradient-blue',
            cancelButton: 'swal-btn-gradient-gray',
            popup: 'swal-popup-rounded'
        },
        buttonsStyling: false
    }).then((result) => {
        if (result.isConfirmed) {
            window.open(printUrl, '_blank');
        }
    });
}
