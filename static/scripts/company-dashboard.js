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
            const createUrl = `/${langCode}/company/qr/create/`;

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
                <div class="row g-3">
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-2">${translations.name}</label>
                        <input type="text" id="swal-user-name" class="form-control form-control-lg" required autocomplete="off">
                    </div>
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-2">${translations.email}</label>
                        <input type="email" id="swal-user-email" class="form-control form-control-lg" required autocomplete="off">
                    </div>
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-2">${translations.password}</label>
                        <input type="password" id="swal-user-password" class="form-control form-control-lg" required autocomplete="new-password">
                    </div>
                </div>
            </div>
        `,
        width: '600px',
        showCancelButton: true,
        confirmButtonText: translations.register,
        cancelButtonText: translations.cancel,
        customClass: {
            confirmButton: 'swal-btn-gradient-green',
            cancelButton: 'swal-btn-gradient-gray',
            popup: 'swal-popup-rounded'
        },
        buttonsStyling: false,
        preConfirm: () => {
            const name = document.getElementById('swal-user-name').value;
            const email = document.getElementById('swal-user-email').value;
            const password = document.getElementById('swal-user-password').value;
            
            if (!name || !email || !password) {
                Swal.showValidationMessage(translations.fillAllFields);
                return false;
            }

            return { name, email, password };
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const data = result.value;
            const langCode = window.location.pathname.split('/')[1];
            const createUrl = `/${langCode}/company/user/create/`;

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

function editUser(userId, name, email) {
    document.getElementById('edit_user_id').value = userId;
    document.getElementById('edit_user_name').value = name;
    document.getElementById('edit_user_email').value = email;
    document.getElementById('edit_user_password').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('editUserModal'));
    modal.show();
}

function updateUser() {
    const userId = document.getElementById('edit_user_id').value;
    const data = {
        name: document.getElementById('edit_user_name').value,
        email: document.getElementById('edit_user_email').value
    };
    
    const password = document.getElementById('edit_user_password').value;
    if (password) {
        data.password = password;
    }

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
            showSuccess(translations.success, translations.userUpdated);
            setTimeout(() => location.reload(), 1500);
        } else {
            showError(translations.error, data.message);
        }
    })
    .catch(error => {
        showError(translations.error, translations.userUpdateFailed);
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
            const deleteUrl = `/${langCode}/company/qr/${qrId}/delete/`;
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
