// Company Dashboard JavaScript Functions

function createQRCode() {
    Swal.fire({
        title: translations.createQRCode,
        html: `
            <div class="container-fluid px-0">
                <div class="row g-3">
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-2">${translations.name}</label>
                        <input type="text" id="swal-qr-name" class="form-control form-control-lg" required>
                    </div>
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-2">${translations.location}</label>
                        <input type="text" id="swal-qr-location" class="form-control form-control-lg" required>
                    </div>
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-2">${translations.additionalInfo}</label>
                        <textarea id="swal-qr-info" class="form-control form-control-lg" rows="3"></textarea>
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
        preConfirm: () => {
            const name = document.getElementById('swal-qr-name').value;
            const location = document.getElementById('swal-qr-location').value;
            const additionalInfo = document.getElementById('swal-qr-info').value;
            
            if (!name || !location) {
                Swal.showValidationMessage(translations.fillAllFields);
                return false;
            }

            return { name, location, additional_info: additionalInfo };
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const data = result.value;
            const langCode = window.location.pathname.split('/')[1];
            const createUrl = `/${langCode}/qr/create/`;

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
                    Swal.fire({
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
                    Swal.fire({
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
                Swal.fire({
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
    Swal.fire({
        title: translations.registerEmployee,
        html: `
            <div class="container-fluid px-0">
                <div class="row g-2">
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-1 small">${translations.name}</label>
                        <input type="text" id="swal-user-name" class="form-control" required autocomplete="off">
                    </div>
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-1 small">${translations.email}</label>
                        <input type="email" id="swal-user-email" class="form-control" required autocomplete="off">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-semibold mb-1 small">${translations.password}</label>
                        <input type="password" id="swal-user-password" class="form-control" required autocomplete="new-password">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-semibold mb-1 small">${translations.confirmPassword}</label>
                        <input type="password" id="swal-user-password-confirm" class="form-control" required autocomplete="new-password">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-semibold mb-1 small">${translations.basicWorkHours}</label>
                        <input type="number" id="swal-user-work-hours" class="form-control" value="160" required min="0" step="1">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-semibold mb-1 small">${translations.holidaysPerYear}</label>
                        <input type="number" id="swal-user-holidays" class="form-control" value="20" required min="0" step="1">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-semibold mb-1 small">${translations.role}</label>
                        <select id="swal-user-role" class="form-select" style="cursor: pointer;">
                            <option value="employee"><i class="fas fa-user"></i> ${translations.employee}</option>
                            <option value="manager"><i class="fas fa-user-tie"></i> ${translations.manager}</option>
                        </select>
                    </div>
                    <div class="col-12 mt-3" id="manager-permissions" style="display: none;">
                        <div class="alert alert-info py-2 px-3 mb-2" style="font-size: 0.875rem;">
                            <i class="fas fa-shield-alt me-1"></i> ${translations.permissions}
                        </div>
                        <div class="d-flex flex-column gap-2">
                            <label class="d-flex align-items-center p-2 border rounded" style="cursor: pointer; transition: all 0.2s;">
                                <input class="form-check-input m-0 me-2" type="checkbox" id="perm-edit-employees" checked>
                                <span style="font-size: 0.9rem;"><i class="fas fa-users text-primary me-2"></i>${translations.canEditEmployees}</span>
                            </label>
                            <label class="d-flex align-items-center p-2 border rounded" style="cursor: pointer; transition: all 0.2s;">
                                <input class="form-check-input m-0 me-2" type="checkbox" id="perm-edit-qr" checked>
                                <span style="font-size: 0.9rem;"><i class="fas fa-qrcode text-success me-2"></i>${translations.canEditQR}</span>
                            </label>
                            <label class="d-flex align-items-center p-2 border rounded" style="cursor: pointer; transition: all 0.2s;">
                                <input class="form-check-input m-0 me-2" type="checkbox" id="perm-edit-absences" checked>
                                <span style="font-size: 0.9rem;"><i class="fas fa-calendar-times text-warning me-2"></i>${translations.canEditAbsences}</span>
                            </label>
                        </div>
                        <div class="mt-3">
                            <label class="d-flex align-items-center p-2 border rounded" style="cursor: pointer; transition: all 0.2s;">
                                <input class="form-check-input m-0 me-2" type="checkbox" id="manager-enable-notifications" checked>
                                <span style="font-size: 0.9rem;"><i class="fas fa-bell text-info me-2"></i>${translations.enableNotifications}</span>
                            </label>
                            <div id="manager-notification-options" class="ms-4 mt-2">
                                <div class="d-flex flex-column gap-1">
                                    <label class="d-flex align-items-center" style="cursor: pointer; font-size: 0.85rem;">
                                        <input class="form-check-input m-0 me-2" type="checkbox" id="manager-notify-arrival" checked style="transform: scale(0.9);">
                                        <span><i class="fas fa-sign-in-alt me-1"></i>${translations.arrival}</span>
                                    </label>
                                    <label class="d-flex align-items-center" style="cursor: pointer; font-size: 0.85rem;">
                                        <input class="form-check-input m-0 me-2" type="checkbox" id="manager-notify-departure" checked style="transform: scale(0.9);">
                                        <span><i class="fas fa-sign-out-alt me-1"></i>${translations.departure}</span>
                                    </label>
                                    <label class="d-flex align-items-center" style="cursor: pointer; font-size: 0.85rem;">
                                        <input class="form-check-input m-0 me-2" type="checkbox" id="manager-notify-lunch-start" checked style="transform: scale(0.9);">
                                        <span><i class="fas fa-utensils me-1"></i>${translations.lunchBreakStart}</span>
                                    </label>
                                    <label class="d-flex align-items-center" style="cursor: pointer; font-size: 0.85rem;">
                                        <input class="form-check-input m-0 me-2" type="checkbox" id="manager-notify-lunch-end" checked style="transform: scale(0.9);">
                                        <span><i class="fas fa-utensils me-1"></i>${translations.lunchBreakEnd}</span>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `,
        width: '550px',
        showCancelButton: true,
        confirmButtonText: translations.register,
        cancelButtonText: translations.cancel,
        customClass: {
            confirmButton: 'swal-btn-gradient-green',
            cancelButton: 'swal-btn-gradient-gray',
            popup: 'swal-popup-rounded'
        },
        buttonsStyling: false,
        didOpen: () => {
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
        preConfirm: () => {
            const name = document.getElementById('swal-user-name').value;
            const email = document.getElementById('swal-user-email').value;
            const password = document.getElementById('swal-user-password').value;
            const passwordConfirm = document.getElementById('swal-user-password-confirm').value;
            const role = document.getElementById('swal-user-role').value;
            const workHours = document.getElementById('swal-user-work-hours').value;
            const holidays = document.getElementById('swal-user-holidays').value;
            
            if (!name || !email || !password || !passwordConfirm || !workHours || !holidays) {
                Swal.showValidationMessage(translations.fillAllFields);
                return false;
            }
            
            if (password.length < 8) {
                Swal.showValidationMessage(translations.passwordMinLength);
                return false;
            }
            
            if (password !== passwordConfirm) {
                Swal.showValidationMessage(translations.passwordsDontMatch);
                return false;
            }

            const data = { name, email, password, basic_work_hours: parseInt(workHours), holidays_per_year: parseInt(holidays), is_manager: role === 'manager' };
            
            if (role === 'manager') {
                data.can_edit_employees = document.getElementById('perm-edit-employees').checked;
                data.can_edit_qr_codes = document.getElementById('perm-edit-qr').checked;
                data.can_edit_absences = document.getElementById('perm-edit-absences').checked;
                
                // Notification preferences
                const enableNotifications = document.getElementById('manager-enable-notifications')?.checked || false;
                data.notify_arrival = enableNotifications && (document.getElementById('manager-notify-arrival')?.checked || false);
                data.notify_departure = enableNotifications && (document.getElementById('manager-notify-departure')?.checked || false);
                data.notify_lunch_break_start = enableNotifications && (document.getElementById('manager-notify-lunch-start')?.checked || false);
                data.notify_lunch_break_end = enableNotifications && (document.getElementById('manager-notify-lunch-end')?.checked || false);
            }

            return data;
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const data = result.value;
            const langCode = window.location.pathname.split('/')[1];
            const createUrl = `/${langCode}/user/create/`;

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
                    Swal.fire({
                        icon: 'success',
                        title: translations.success,
                        text: translations.userRegistered,
                        customClass: {
                            confirmButton: 'swal-btn-gradient-green',
                            popup: 'swal-popup-rounded'
                        },
                        buttonsStyling: false
                    }).then(() => {
                        location.reload();
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: translations.error,
                        text: data.message || translations.userRegisterFailed,
                        customClass: {
                            confirmButton: 'swal-btn-gradient-red',
                            popup: 'swal-popup-rounded'
                        },
                        buttonsStyling: false
                    });
                }
            })
            .catch(error => {
                Swal.fire({
                    icon: 'error',
                    title: translations.error,
                    text: translations.userRegisterFailed,
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

function editUser(userId, name, email, basicWorkHours, holidaysPerYear, isManager, canEditEmployees, canEditQR, canEditAbsences, notifyArrival, notifyDeparture, notifyLunchStart, notifyLunchEnd) {
    // Determine if notifications are enabled (any notification is checked)
    const notificationsEnabled = notifyArrival || notifyDeparture || notifyLunchStart || notifyLunchEnd;
    
    Swal.fire({
        title: translations.editEmployee,
        html: `
            <div class="container-fluid px-0">
                <div class="row g-2">
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-1 small">${translations.name}</label>
                        <input type="text" id="swal-edit-user-name" class="form-control" value="${name}" required autocomplete="off">
                    </div>
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-1 small">${translations.email}</label>
                        <input type="email" id="swal-edit-user-email" class="form-control" value="${email}" required autocomplete="off">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-semibold mb-1 small">${translations.newPassword}</label>
                        <input type="password" id="swal-edit-user-password" class="form-control" autocomplete="new-password">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-semibold mb-1 small">${translations.confirmPassword}</label>
                        <input type="password" id="swal-edit-user-password-confirm" class="form-control" autocomplete="new-password">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-semibold mb-1 small">${translations.basicWorkHours}</label>
                        <input type="number" id="swal-edit-user-work-hours" class="form-control" value="${basicWorkHours || 160}" required min="0" step="1">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-semibold mb-1 small">${translations.holidaysPerYear}</label>
                        <input type="number" id="swal-edit-user-holidays" class="form-control" value="${holidaysPerYear || 20}" required min="0" step="1">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label fw-semibold mb-1 small">${translations.role}</label>
                        <select id="swal-edit-user-role" class="form-select" style="cursor: pointer;">
                            <option value="employee" ${!isManager ? 'selected' : ''}><i class="fas fa-user"></i> ${translations.employee}</option>
                            <option value="manager" ${isManager ? 'selected' : ''}><i class="fas fa-user-tie"></i> ${translations.manager}</option>
                        </select>
                    </div>
                    <div class="col-12 mt-3" id="edit-manager-permissions" style="display: ${isManager ? 'block' : 'none'};">
                        <div class="alert alert-info py-2 px-3 mb-2" style="font-size: 0.875rem;">
                            <i class="fas fa-shield-alt me-1"></i> ${translations.permissions}
                        </div>
                        <div class="d-flex flex-column gap-2">
                            <label class="d-flex align-items-center p-2 border rounded" style="cursor: pointer; transition: all 0.2s;">
                                <input class="form-check-input m-0 me-2" type="checkbox" id="edit-perm-edit-employees" ${canEditEmployees ? 'checked' : ''}>
                                <span style="font-size: 0.9rem;"><i class="fas fa-users text-primary me-2"></i>${translations.canEditEmployees}</span>
                            </label>
                            <label class="d-flex align-items-center p-2 border rounded" style="cursor: pointer; transition: all 0.2s;">
                                <input class="form-check-input m-0 me-2" type="checkbox" id="edit-perm-edit-qr" ${canEditQR ? 'checked' : ''}>
                                <span style="font-size: 0.9rem;"><i class="fas fa-qrcode text-success me-2"></i>${translations.canEditQR}</span>
                            </label>
                            <label class="d-flex align-items-center p-2 border rounded" style="cursor: pointer; transition: all 0.2s;">
                                <input class="form-check-input m-0 me-2" type="checkbox" id="edit-perm-edit-absences" ${canEditAbsences ? 'checked' : ''}>
                                <span style="font-size: 0.9rem;"><i class="fas fa-calendar-times text-warning me-2"></i>${translations.canEditAbsences}</span>
                            </label>
                        </div>
                        <div class="mt-3">
                            <label class="d-flex align-items-center p-2 border rounded" style="cursor: pointer; transition: all 0.2s;">
                                <input class="form-check-input m-0 me-2" type="checkbox" id="edit-manager-enable-notifications" ${notificationsEnabled ? 'checked' : ''}>
                                <span style="font-size: 0.9rem;"><i class="fas fa-bell text-info me-2"></i>${translations.enableNotifications}</span>
                            </label>
                            <div id="edit-manager-notification-options" class="ms-4 mt-2" style="display: ${notificationsEnabled ? 'block' : 'none'};">
                                <div class="d-flex flex-column gap-1">
                                    <label class="d-flex align-items-center" style="cursor: pointer; font-size: 0.85rem;">
                                        <input class="form-check-input m-0 me-2" type="checkbox" id="edit-manager-notify-arrival" ${notifyArrival ? 'checked' : ''} style="transform: scale(0.9);">
                                        <span><i class="fas fa-sign-in-alt me-1"></i>${translations.arrival}</span>
                                    </label>
                                    <label class="d-flex align-items-center" style="cursor: pointer; font-size: 0.85rem;">
                                        <input class="form-check-input m-0 me-2" type="checkbox" id="edit-manager-notify-departure" ${notifyDeparture ? 'checked' : ''} style="transform: scale(0.9);">
                                        <span><i class="fas fa-sign-out-alt me-1"></i>${translations.departure}</span>
                                    </label>
                                    <label class="d-flex align-items-center" style="cursor: pointer; font-size: 0.85rem;">
                                        <input class="form-check-input m-0 me-2" type="checkbox" id="edit-manager-notify-lunch-start" ${notifyLunchStart ? 'checked' : ''} style="transform: scale(0.9);">
                                        <span><i class="fas fa-utensils me-1"></i>${translations.lunchBreakStart}</span>
                                    </label>
                                    <label class="d-flex align-items-center" style="cursor: pointer; font-size: 0.85rem;">
                                        <input class="form-check-input m-0 me-2" type="checkbox" id="edit-manager-notify-lunch-end" ${notifyLunchEnd ? 'checked' : ''} style="transform: scale(0.9);">
                                        <span><i class="fas fa-utensils me-1"></i>${translations.lunchBreakEnd}</span>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `,
        width: '550px',
        showCancelButton: true,
        confirmButtonText: translations.save,
        cancelButtonText: translations.cancel,
        customClass: {
            confirmButton: 'swal-btn-gradient-green',
            cancelButton: 'swal-btn-gradient-gray',
            popup: 'swal-popup-rounded'
        },
        buttonsStyling: false,
        didOpen: () => {
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
        preConfirm: () => {
            const name = document.getElementById('swal-edit-user-name').value;
            const email = document.getElementById('swal-edit-user-email').value;
            const password = document.getElementById('swal-edit-user-password').value;
            const passwordConfirm = document.getElementById('swal-edit-user-password-confirm').value;
            const workHours = document.getElementById('swal-edit-user-work-hours').value;
            const holidays = document.getElementById('swal-edit-user-holidays').value;
            const role = document.getElementById('swal-edit-user-role').value;
            
            if (!name || !email || !workHours || !holidays) {
                Swal.showValidationMessage(translations.fillAllFields);
                return false;
            }
            
            // Validate password only if provided
            if (password || passwordConfirm) {
                if (password.length < 8) {
                    Swal.showValidationMessage(translations.passwordMinLength);
                    return false;
                }
                
                if (password !== passwordConfirm) {
                    Swal.showValidationMessage(translations.passwordsDontMatch);
                    return false;
                }
            }

            const data = { name, email, basic_work_hours: parseInt(workHours), holidays_per_year: parseInt(holidays), is_manager: role === 'manager' };
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
                data.notify_lunch_break_start = enableNotifications && (document.getElementById('edit-manager-notify-lunch-start')?.checked || false);
                data.notify_lunch_break_end = enableNotifications && (document.getElementById('edit-manager-notify-lunch-end')?.checked || false);
            }

            return data;
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const data = result.value;
            const langCode = window.location.pathname.split('/')[1];
            const editUrl = `/${langCode}/company/user/${userId}/edit/`;
            
            fetch(editUrl, {
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
                    Swal.fire({
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
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: translations.error,
                        text: data.message || translations.userUpdateFailed,
                        customClass: {
                            confirmButton: 'swal-btn-gradient-red',
                            popup: 'swal-popup-rounded'
                        },
                        buttonsStyling: false
                    });
                }
            })
            .catch(error => {
                Swal.fire({
                    icon: 'error',
                    title: translations.error,
                    text: translations.userUpdateFailed,
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

function deleteUser(userId, userName) {
    console.log('deleteUser called:', userId, userName);
    confirmDelete(userName, 'User').then((result) => {
        console.log('Swal result:', result);
        if (result.isConfirmed) {
            const langCode = window.location.pathname.split('/')[1];
            const deleteUrl = `/${langCode}/company/user/${userId}/delete/`;
            console.log('Delete URL:', deleteUrl);
            console.log('CSRF Token:', csrfToken);
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
    
    Swal.fire({
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
