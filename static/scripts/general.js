function openAddQRCodeModal() {
    Swal.fire({
        title: 'Add QR Code',
        html: `
            <div class="mb-3 text-start" style="width: 90%; margin: auto;">
                <label for="swal-input-name" class="form-label">Name & Surname</label>
                <input type="text" id="swal-input-name" class="form-control"  placeholder="Enter Name and Surname" required>
            </div>
            <div class="mb-3 text-start" style="width: 90%; margin: auto;">
                <label for="swal-input-id-card" class="form-label">ID card</label>
                <input type="email" id="swal-input-id-card" class="form-control"  placeholder="Enter ID card" required>
            </div>
            <div class="mb-3 text-start" style="width: 90%; margin: auto;">
                <label for="swal-input-email" class="form-label">Email</label>
                <input type="email" id="swal-input-email" class="form-control"  placeholder="Enter email" required>
            </div>
            <div class="mb-3 text-start" style="width: 90%; margin: auto;">
                <label for="swal-input-phone" class="form-label">Phone</label>
                <input type="text" id="swal-input-phone" class="form-control"  placeholder="Enter phone" required>
            </div>
            <div class="mb-3 text-start" style="width: 90%; margin: auto;">
                <label for="swal-input-company" class="form-label">Company</label>
                <input type="text" id="swal-input-company" class="form-control"  placeholder="Enter company" required>
            </div>
        `,
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: 'Submit',
        preConfirm: () => {
            const name = document.getElementById('swal-input-name').value.trim();
            const email = document.getElementById('swal-input-email').value.trim();
            const phone = document.getElementById('swal-input-phone').value.trim();
            const company = document.getElementById('swal-input-company').value.trim();
            const id_card = document.getElementById('swal-input-id-card').value.trim();

            if (!name || !email || !phone || !company || !id_card) {
                Swal.showValidationMessage('All fields are required.');
                return false;
            }

            // Additional validation can be added here (like regex)
            return { name, email, phone, company, id_card };
        }
    }).then((result) => {
        if (result.isConfirmed) {
            fetch('/add_qr_code/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(result.value)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    Swal.fire('Success', 'QR Code added successfully!', 'success')
                        .then(() => location.reload());
                } else {
                    Swal.fire('Error', data.error || 'Something went wrong.', 'error');
                }
            })
            .catch(err => {
                console.error(err);
                Swal.fire('Error', 'Failed to submit form.', 'error');
            });
        }
    });
}