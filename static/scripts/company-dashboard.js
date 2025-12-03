// Company Dashboard JavaScript Functions

function createQRCode() {
    const data = {
        name: document.getElementById('qr_name').value,
        location: document.getElementById('qr_location').value,
        additional_info: document.getElementById('qr_info').value
    };

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
            showSuccess(translations.success, translations.qrCodeCreated);
            setTimeout(() => location.reload(), 1500);
        } else {
            showError(translations.error, data.message);
        }
    })
    .catch(error => {
        showError(translations.error, translations.qrCodeCreateFailed);
    });
}

function createUser() {
    const data = {
        name: document.getElementById('user_name').value,
        email: document.getElementById('user_email').value,
        password: document.getElementById('user_password').value
    };

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
            showSuccess(translations.success, translations.userRegistered);
            setTimeout(() => location.reload(), 1500);
        } else {
            showError(translations.error, data.message);
        }
    })
    .catch(error => {
        showError(translations.error, translations.userRegisterFailed);
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
