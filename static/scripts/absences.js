const t = {
    addAbsence: translations.addAbsence || "Add Absence",
    editAbsence: translations.editAbsence || "Edit Absence",
    deleteAbsence: translations.deleteAbsence || "Delete Absence",
    selectEmployee: translations.selectEmployee || "Select employee",
    employee: translations.employee || "Employee",
    dateRange: translations.dateRange || "Period",
    cancel: translations.cancel || "Cancel",
    save: translations.save || "Save",
    delete: translations.delete || "Delete",
    confirmDeleteText: translations.confirmDeleteText || "Absence for employee",
    willBeDeleted: translations.willBeDeleted || "will be deleted",
    yes: translations.yes || "Yes",
    no: translations.no || "No",
    success: translations.success || "Success",
    error: translations.error || "Error",
    absenceAdded: translations.absenceAdded || "Absence successfully added",
    absenceUpdated: translations.absenceUpdated || "Absence successfully updated",
    absenceDeleted: translations.absenceDeleted || "Absence successfully deleted",
    absenceAddFailed: translations.absenceAddFailed || "Failed to add absence",
    absenceUpdateFailed: translations.absenceUpdateFailed || "Failed to update absence",
    absenceDeleteFailed: translations.absenceDeleteFailed || "Failed to delete absence",
    fillAllFields: translations.fillAllFields || "Please fill all fields",
    invalidDateRange: translations.invalidDateRange || "Invalid date range",
    selectDates: translations.selectDates || "Select dates",
    timeFrom: translations.timeFrom || "Time from",
    timeTo: translations.timeTo || "Time to",
    timeOptional: translations.timeOptional || "Optional for single-day absences",
    type: translations.absenceType || "Type",
    vacation: translations.absenceVacation || "Vacation",
    sickLeave: translations.sickLeave || "Sick Leave",
    doctor: translations.doctor || "Doctor",
    homeOffice: translations.homeOffice || "Home Office",
    selectType: translations.selectType || "Select type",
    approveAbsence: translations.approveAbsence || "Approve Absence",
    confirmApproveText: translations.confirmApproveText || "Are you sure you want to approve absence for",
    yesApprove: translations.yesApprove || "Yes, approve",
    absenceApproved: translations.absenceApproved || "Absence successfully approved",
    absenceApproveFailed: translations.absenceApproveFailed || "Failed to approve absence",
    addingAbsence: translations.addingAbsence || "Adding absence...",
    updatingAbsence: translations.updatingAbsence || "Updating absence...",
    deletingAbsence: translations.deletingAbsence || "Deleting absence...",
    approvingAbsence: translations.approvingAbsence || "Approving absence..."
};
// Build custom type picker HTML (replaces native <select> for absence type)
function buildTypePickerHTML(idSuffix, selectedValue) {
    const types = [
        { value: 'vacation',    icon: 'fas fa-umbrella-beach', cls: 'type-vacation',    label: () => t.vacation },
        { value: 'sick_leave',  icon: 'fas fa-notes-medical',  cls: 'type-sick_leave',  label: () => t.sickLeave },
        { value: 'doctor',      icon: 'fas fa-user-doctor',    cls: 'type-doctor',      label: () => t.doctor },
        { value: 'home_office', icon: 'fas fa-home',           cls: 'type-home_office', label: () => t.homeOffice || 'Home Office' }
    ];
    const buttons = types.map(tp =>
        `<button type="button" class="swal-type-btn ${tp.cls}${selectedValue === tp.value ? ' selected' : ''}" data-type="${tp.value}">
            <i class="${tp.icon} swal-type-icon"></i>
            <span class="swal-type-label">${tp.label()}</span>
        </button>`
    ).join('');
    return `<input type="hidden" id="swal-type-${idSuffix}" value="${selectedValue || ''}">
        <div class="swal-type-grid">${buttons}</div>`;
}

function initTypePicker(idSuffix) {
    const hidden = document.getElementById(`swal-type-${idSuffix}`);
    document.querySelectorAll('.swal-type-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.swal-type-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            hidden.value = btn.dataset.type;
        });
    });
}

// Initialize daterangepicker for modal (uses global daterangepickerLocale from base.html)
function initModalDateRangePicker(inputId, callback) {
    const locale = daterangepickerLocale[langCode] || daterangepickerLocale.sk;

    $(`#${inputId}`).daterangepicker({
        locale: locale,
        autoUpdateInput: false,
        opens: 'center'
    });

    $(`#${inputId}`).on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('DD.MM.YYYY') + ' - ' + picker.endDate.format('DD.MM.YYYY'));
        if (callback) {
            callback(picker.startDate, picker.endDate);
        }
    });

    $(`#${inputId}`).on('cancel.daterangepicker', function(ev, picker) {
        $(this).val('');
    });
}
// Add Vacation
function addVacation(users) {
    let selectedUserId = null;
    let startDate = null;
    let endDate = null;

    // Create employee select options
    let employeeOptions = `<option value="">${t.selectEmployee}</option>`;
    users.forEach(user => {
        employeeOptions += `<option value="${user.id}">${user.name}</option>`;
    });

    appUI.fire({
        icon: 'info',
        title: t.addAbsence,
        html: `
            <div class="swal-form-layout">
                <div class="swal-form-section">
                    <div class="swal-form-section-title">
                        <span class="swal-form-section-icon">
                            <i class="fas fa-user"></i>
                        </span>
                        <span>${t.employee}</span>
                    </div>
                    <div class="swal-form-field">
                        <select id="swal-employee" class="form-select" style="cursor: pointer;">
                            ${employeeOptions}
                        </select>
                    </div>
                </div>
                    
                <div class="swal-form-section">
                    <div class="swal-form-section-title">
                        <span class="swal-form-section-icon">
                            <i class="fas fa-tag"></i>
                        </span>
                        <span>${t.type}</span>
                    </div>
                    <div class="swal-form-field">
                        ${buildTypePickerHTML('main', '')}
                    </div>
                </div>
                    
                <div class="swal-form-section">
                    <div class="swal-form-section-title">
                        <span class="swal-form-section-icon">
                            <i class="fas fa-calendar-alt"></i>
                        </span>
                        <span>${t.dateRange}</span>
                    </div>
                    <div class="swal-form-field">
                        <input type="text" id="swal-daterange" class="form-control" readonly placeholder="${t.selectDates}" style="cursor: pointer; background-color: white;">
                    </div>
                </div>
                    
                <div class="swal-form-section swal-form-transition" id="time-fields" style="display: none; opacity: 0;">
                    <div class="swal-form-section-title">
                        <span class="swal-form-section-icon">
                            <i class="fas fa-clock"></i>
                        </span>
                        <span>${t.timeOptional}</span>
                    </div>
                    <div class="swal-form-card">
                        <div class="swal-form-card-header">
                            <i class="fas fa-info-circle"></i>
                            <span>${t.timeOptional}</span>
                        </div>
                        <div class="swal-form-inline">
                            <div class="swal-form-field">
                                <label class="form-label" for="swal-time-from">${t.timeFrom}</label>
                                <input type="time" id="swal-time-from" class="form-control">
                            </div>
                            <div class="swal-form-field">
                                <label class="form-label" for="swal-time-to">${t.timeTo}</label>
                                <input type="time" id="swal-time-to" class="form-control">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `,
        width: '600px',
        showCancelButton: true,
        confirmButtonText: t.save,
        cancelButtonText: t.cancel,
        customClass: {
            confirmButton: 'swal-btn-primary',
            cancelButton: 'swal-btn-secondary',
            popup: 'swal-popup-rounded'
        },
        buttonsStyling: false,
        didOpen: () => {
            document.getElementById('swal-employee').focus();
            initTypePicker('main');

            initModalDateRangePicker('swal-daterange', (start, end) => {
                startDate = start.format('YYYY-MM-DD');
                endDate = end.format('YYYY-MM-DD');
                
                const timeFields = document.getElementById('time-fields');
                
                // Show time fields with smooth animation for single-day absences
                if (startDate === endDate) {
                    timeFields.style.display = 'block';
                    setTimeout(() => {
                        timeFields.style.opacity = '1';
                    }, 10);
                } else {
                    timeFields.style.opacity = '0';
                    setTimeout(() => {
                        timeFields.style.display = 'none';
                        document.getElementById('swal-time-from').value = '';
                        document.getElementById('swal-time-to').value = '';
                    }, 300);
                }
            });
        },
        preConfirm: () => {
            selectedUserId = document.getElementById('swal-employee').value;
            const selectedType = document.getElementById('swal-type-main').value;
            const timeFrom = document.getElementById('swal-time-from').value;
            const timeTo = document.getElementById('swal-time-to').value;
            
            if (!selectedUserId || !selectedType || !startDate || !endDate) {
                appUI.showValidationMessage(t.fillAllFields);
                return false;
            }

            if (new Date(endDate) < new Date(startDate)) {
                appUI.showValidationMessage(t.invalidDateRange);
                return false;
            }

            const result = { userId: selectedUserId, dateFrom: startDate, dateTo: endDate, type: selectedType };
            
            // Add time fields only if both are provided and it's a single day
            if (startDate === endDate && timeFrom && timeTo) {
                result.timeFrom = timeFrom;
                result.timeTo = timeTo;
            }
            
            return result;
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const data = result.value;
            
            appUI.fire({
                title: t.addingAbsence,
                allowOutsideClick: false,
                allowEscapeKey: false,
                didOpen: () => {
                    appUI.showLoading();
                }
            });
            
            fetch(`/${langCode}/absence/create/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    user_id: data.userId,
                    date_from: data.dateFrom,
                    date_to: data.dateTo,
                    type: data.type,
                    time_from: data.timeFrom,
                    time_to: data.timeTo
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    appUI.fire({
                        icon: 'success',
                        title: t.success,
                        text: t.absenceAdded,
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
                        title: t.error,
                        text: data.message || t.absenceAddFailed,
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
                    title: t.error,
                    text: t.absenceAddFailed,
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

// Edit Vacation
function editVacation(vacationId, currentUserId, currentUserName, currentDateFrom, currentDateTo, currentType, currentTimeFrom, currentTimeTo, users) {
    let selectedUserId = currentUserId;
    let startDate = currentDateFrom;
    let endDate = currentDateTo;

    // Create employee select options
    let employeeOptions = '';
    
    // Check if users array is provided, if not use current user only
    if (!users || !Array.isArray(users)) {
        users = [{ id: currentUserId, name: currentUserName }];
    }
    
    users.forEach(user => {
        const selected = user.id === currentUserId ? 'selected' : '';
        employeeOptions += `<option value="${user.id}" ${selected}>${user.name}</option>`;
    });

    // Format dates for display
    const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('sk-SK');
    };

    const displayRange = `${formatDate(currentDateFrom)} - ${formatDate(currentDateTo)}`;
    
    // Check if single day for showing time fields
    const isSingleDay = currentDateFrom === currentDateTo;

    appUI.fire({
        icon: 'info',
        title: t.editAbsence,
        html: `
            <div class="swal-form-layout">
                <div class="swal-form-section">
                    <div class="swal-form-section-title">
                        <span class="swal-form-section-icon"><i class="fas fa-user"></i></span>
                        <span>${t.employee}</span>
                    </div>
                    <div class="swal-form-field">
                        <select id="swal-employee" class="form-select" style="cursor:pointer;">
                            ${employeeOptions}
                        </select>
                    </div>
                </div>
                <div class="swal-form-section">
                    <div class="swal-form-section-title">
                        <span class="swal-form-section-icon"><i class="fas fa-tag"></i></span>
                        <span>${t.type}</span>
                    </div>
                    <div class="swal-form-field">
                        ${buildTypePickerHTML('edit', currentType)}
                    </div>
                </div>
                <div class="swal-form-section">
                    <div class="swal-form-section-title">
                        <span class="swal-form-section-icon"><i class="fas fa-calendar-alt"></i></span>
                        <span>${t.dateRange}</span>
                    </div>
                    <div class="swal-form-field">
                        <input type="text" id="swal-daterange" class="form-control" readonly placeholder="${t.selectDates}" value="${displayRange}" style="cursor:pointer;">
                    </div>
                </div>
                <div class="swal-form-section swal-form-transition" id="time-fields-edit" style="display:${isSingleDay ? 'block' : 'none'}; opacity:${isSingleDay ? '1' : '0'};">
                    <div class="swal-form-section-title">
                        <span class="swal-form-section-icon"><i class="fas fa-clock"></i></span>
                        <span>${t.timeOptional}</span>
                    </div>
                    <div class="swal-form-inline">
                        <div class="swal-form-field">
                            <label class="form-label" for="swal-time-from-edit">${t.timeFrom}</label>
                            <input type="time" id="swal-time-from-edit" class="form-control" value="${currentTimeFrom || ''}">
                        </div>
                        <div class="swal-form-field">
                            <label class="form-label" for="swal-time-to-edit">${t.timeTo}</label>
                            <input type="time" id="swal-time-to-edit" class="form-control" value="${currentTimeTo || ''}">
                        </div>
                    </div>
                </div>
            </div>
        `,
        width: '560px',
        showCancelButton: true,
        confirmButtonText: t.save,
        cancelButtonText: t.cancel,
        customClass: {
            confirmButton: 'swal-btn-primary',
            cancelButton: 'swal-btn-secondary',
            popup: 'swal-popup-rounded'
        },
        buttonsStyling: false,
        didOpen: () => {
            initTypePicker('edit');
            initModalDateRangePicker('swal-daterange', (start, end) => {
                startDate = start.format('YYYY-MM-DD');
                endDate = end.format('YYYY-MM-DD');
                
                const timeFields = document.getElementById('time-fields-edit');
                
                // Show/hide time fields with smooth animation based on date range
                if (startDate === endDate) {
                    timeFields.style.display = 'block';
                    setTimeout(() => {
                        timeFields.style.opacity = '1';
                    }, 10);
                } else {
                    timeFields.style.opacity = '0';
                    setTimeout(() => {
                        timeFields.style.display = 'none';
                        document.getElementById('swal-time-from-edit').value = '';
                        document.getElementById('swal-time-to-edit').value = '';
                    }, 300);
                }
            });
        },
        preConfirm: () => {
            selectedUserId = document.getElementById('swal-employee').value;
            const selectedType = document.getElementById('swal-type-edit').value;
            const timeFrom = document.getElementById('swal-time-from-edit').value;
            const timeTo = document.getElementById('swal-time-to-edit').value;
            
            if (!selectedUserId || !selectedType || !startDate || !endDate) {
                appUI.showValidationMessage(t.fillAllFields);
                return false;
            }

            if (new Date(endDate) < new Date(startDate)) {
                appUI.showValidationMessage(t.invalidDateRange);
                return false;
            }

            const result = { userId: selectedUserId, dateFrom: startDate, dateTo: endDate, type: selectedType };
            
            // Add time fields only if both are provided and it's a single day
            if (startDate === endDate && timeFrom && timeTo) {
                result.timeFrom = timeFrom;
                result.timeTo = timeTo;
            }
            
            return result;
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const data = result.value;
            
            appUI.fire({
                title: t.updatingAbsence,
                allowOutsideClick: false,
                allowEscapeKey: false,
                didOpen: () => {
                    appUI.showLoading();
                }
            });
            
            fetch(`/${langCode}/absence/${vacationId}/edit/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    user_id: data.userId,
                    date_from: data.dateFrom,
                    date_to: data.dateTo,
                    type: data.type,
                    time_from: data.timeFrom,
                    time_to: data.timeTo
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    appUI.fire({
                        icon: 'success',
                        title: t.success,
                        text: t.absenceUpdated,
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
                        title: t.error,
                        text: data.message || t.absenceUpdateFailed,
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
                    title: t.error,
                    text: t.absenceUpdateFailed,
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

// Add Vacation for specific user (for user details page)
function addVacationForUser(userId, userName) {
    let startDate = null;
    let endDate = null;

    appUI.fire({
        icon: 'info',
        title: t.addAbsence,
        html: `
            <div class="swal-form-layout">
                <div class="swal-form-section">
                    <div class="swal-form-section-title">
                        <span class="swal-form-section-icon"><i class="fas fa-user"></i></span>
                        <span>${t.employee}</span>
                    </div>
                    <div class="swal-form-field">
                        <input type="text" class="form-control" value="${userName}" readonly disabled>
                    </div>
                </div>
                <div class="swal-form-section">
                    <div class="swal-form-section-title">
                        <span class="swal-form-section-icon"><i class="fas fa-tag"></i></span>
                        <span>${t.type}</span>
                    </div>
                    <div class="swal-form-field">
                        ${buildTypePickerHTML('user', '')}
                    </div>
                </div>
                <div class="swal-form-section">
                    <div class="swal-form-section-title">
                        <span class="swal-form-section-icon"><i class="fas fa-calendar-alt"></i></span>
                        <span>${t.dateRange}</span>
                    </div>
                    <div class="swal-form-field">
                        <input type="text" id="swal-daterange-user" class="form-control" readonly placeholder="${t.selectDates}" style="cursor:pointer;">
                    </div>
                </div>
                <div class="swal-form-section swal-form-transition" id="time-fields-user" style="display:none; opacity:0;">
                    <div class="swal-form-section-title">
                        <span class="swal-form-section-icon"><i class="fas fa-clock"></i></span>
                        <span>${t.timeOptional}</span>
                    </div>
                    <div class="swal-form-inline">
                        <div class="swal-form-field">
                            <label class="form-label" for="swal-time-from-user">${t.timeFrom}</label>
                            <input type="time" id="swal-time-from-user" class="form-control">
                        </div>
                        <div class="swal-form-field">
                            <label class="form-label" for="swal-time-to-user">${t.timeTo}</label>
                            <input type="time" id="swal-time-to-user" class="form-control">
                        </div>
                    </div>
                </div>
            </div>
        `,
        width: '560px',
        showCancelButton: true,
        confirmButtonText: t.save,
        cancelButtonText: t.cancel,
        customClass: {
            confirmButton: 'swal-btn-primary',
            cancelButton: 'swal-btn-secondary',
            popup: 'swal-popup-rounded'
        },
        buttonsStyling: false,
        didOpen: () => {
            initTypePicker('user');
            initModalDateRangePicker('swal-daterange-user', (start, end) => {
                startDate = start.format('YYYY-MM-DD');
                endDate = end.format('YYYY-MM-DD');
                
                const timeFields = document.getElementById('time-fields-user');
                
                // Show time fields with smooth animation for single-day absences
                if (startDate === endDate) {
                    timeFields.style.display = 'block';
                    setTimeout(() => {
                        timeFields.style.opacity = '1';
                    }, 10);
                } else {
                    timeFields.style.opacity = '0';
                    setTimeout(() => {
                        timeFields.style.display = 'none';
                        document.getElementById('swal-time-from-user').value = '';
                        document.getElementById('swal-time-to-user').value = '';
                    }, 300);
                }
            });
        },
        preConfirm: () => {
            const selectedType = document.getElementById('swal-type-user').value;
            const timeFrom = document.getElementById('swal-time-from-user').value;
            const timeTo = document.getElementById('swal-time-to-user').value;
            
            if (!selectedType || !startDate || !endDate) {
                appUI.showValidationMessage(t.fillAllFields);
                return false;
            }

            if (new Date(endDate) < new Date(startDate)) {
                appUI.showValidationMessage(t.invalidDateRange);
                return false;
            }

            const result = { userId: userId, dateFrom: startDate, dateTo: endDate, type: selectedType };
            
            // Add time fields only if both are provided and it's a single day
            if (startDate === endDate && timeFrom && timeTo) {
                result.timeFrom = timeFrom;
                result.timeTo = timeTo;
            }
            
            return result;
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const data = result.value;
            
            appUI.fire({
                title: t.addingAbsence,
                allowOutsideClick: false,
                allowEscapeKey: false,
                didOpen: () => {
                    appUI.showLoading();
                }
            });
            
            fetch(`/${langCode}/absence/create/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    user_id: data.userId,
                    date_from: data.dateFrom,
                    date_to: data.dateTo,
                    type: data.type,
                    time_from: data.timeFrom,
                    time_to: data.timeTo
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    appUI.fire({
                        icon: 'success',
                        title: t.success,
                        text: t.absenceAdded,
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
                        title: t.error,
                        text: data.message || t.absenceAddFailed,
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
                    title: t.error,
                    text: t.absenceAddFailed,
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

// Edit Vacation Simple (without employee selector - for user details page)
function editVacationSimple(vacationId, userId, userName, currentDateFrom, currentDateTo, currentType, currentTimeFrom, currentTimeTo) {
    let startDate = currentDateFrom;
    let endDate = currentDateTo;

    // Format dates for display
    const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('sk-SK');
    };

    const displayRange = `${formatDate(currentDateFrom)} - ${formatDate(currentDateTo)}`;
    
    // Check if single day for showing time fields
    const isSingleDay = currentDateFrom === currentDateTo;

    appUI.fire({
        icon: 'info',
        title: t.editAbsence,
        html: `
            <div class="swal-form-layout">
                <div class="swal-form-section">
                    <div class="swal-form-section-title">
                        <span class="swal-form-section-icon"><i class="fas fa-user"></i></span>
                        <span>${t.employee}</span>
                    </div>
                    <div class="swal-form-field">
                        <input type="text" class="form-control" value="${userName}" readonly disabled>
                    </div>
                </div>
                <div class="swal-form-section">
                    <div class="swal-form-section-title">
                        <span class="swal-form-section-icon"><i class="fas fa-tag"></i></span>
                        <span>${t.type}</span>
                    </div>
                    <div class="swal-form-field">
                        ${buildTypePickerHTML('simple', currentType)}
                    </div>
                </div>
                <div class="swal-form-section">
                    <div class="swal-form-section-title">
                        <span class="swal-form-section-icon"><i class="fas fa-calendar-alt"></i></span>
                        <span>${t.dateRange}</span>
                    </div>
                    <div class="swal-form-field">
                        <input type="text" id="swal-daterange-simple" class="form-control" readonly placeholder="${t.selectDates}" value="${displayRange}" style="cursor:pointer;">
                    </div>
                </div>
                <div class="swal-form-section swal-form-transition" id="time-fields-simple" style="display:${isSingleDay ? 'block' : 'none'}; opacity:${isSingleDay ? '1' : '0'};">
                    <div class="swal-form-section-title">
                        <span class="swal-form-section-icon"><i class="fas fa-clock"></i></span>
                        <span>${t.timeOptional}</span>
                    </div>
                    <div class="swal-form-inline">
                        <div class="swal-form-field">
                            <label class="form-label" for="swal-time-from-simple">${t.timeFrom}</label>
                            <input type="time" id="swal-time-from-simple" class="form-control" value="${currentTimeFrom || ''}">
                        </div>
                        <div class="swal-form-field">
                            <label class="form-label" for="swal-time-to-simple">${t.timeTo}</label>
                            <input type="time" id="swal-time-to-simple" class="form-control" value="${currentTimeTo || ''}">
                        </div>
                    </div>
                </div>
            </div>
        `,
        width: '560px',
        showCancelButton: true,
        confirmButtonText: t.save,
        cancelButtonText: t.cancel,
        customClass: {
            confirmButton: 'swal-btn-primary',
            cancelButton: 'swal-btn-secondary',
            popup: 'swal-popup-rounded'
        },
        buttonsStyling: false,
        didOpen: () => {
            initTypePicker('simple');
            initModalDateRangePicker('swal-daterange-simple', (start, end) => {
                startDate = start.format('YYYY-MM-DD');
                endDate = end.format('YYYY-MM-DD');
                
                const timeFields = document.getElementById('time-fields-simple');
                
                // Show/hide time fields with smooth animation based on date range
                if (startDate === endDate) {
                    timeFields.style.display = 'block';
                    setTimeout(() => {
                        timeFields.style.opacity = '1';
                    }, 10);
                } else {
                    timeFields.style.opacity = '0';
                    setTimeout(() => {
                        timeFields.style.display = 'none';
                        document.getElementById('swal-time-from-simple').value = '';
                        document.getElementById('swal-time-to-simple').value = '';
                    }, 300);
                }
            });
        },
        preConfirm: () => {
            const selectedType = document.getElementById('swal-type-simple').value;
            const timeFrom = document.getElementById('swal-time-from-simple').value;
            const timeTo = document.getElementById('swal-time-to-simple').value;
            
            if (!selectedType || !startDate || !endDate) {
                appUI.showValidationMessage(t.fillAllFields);
                return false;
            }

            if (new Date(endDate) < new Date(startDate)) {
                appUI.showValidationMessage(t.invalidDateRange);
                return false;
            }

            const result = { userId: userId, dateFrom: startDate, dateTo: endDate, type: selectedType };
            
            // Add time fields only if both are provided and it's a single day
            if (startDate === endDate && timeFrom && timeTo) {
                result.timeFrom = timeFrom;
                result.timeTo = timeTo;
            }
            
            return result;
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const data = result.value;
            
            appUI.fire({
                title: t.updatingAbsence,
                allowOutsideClick: false,
                allowEscapeKey: false,
                didOpen: () => {
                    appUI.showLoading();
                }
            });
            
            fetch(`/${langCode}/absence/${vacationId}/edit/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    user_id: data.userId,
                    date_from: data.dateFrom,
                    date_to: data.dateTo,
                    type: data.type,
                    time_from: data.timeFrom,
                    time_to: data.timeTo
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    appUI.fire({
                        icon: 'success',
                        title: t.success,
                        text: t.absenceUpdated,
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
                        title: t.error,
                        text: data.message || t.absenceUpdateFailed,
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
                    title: t.error,
                    text: t.absenceUpdateFailed,
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

// Delete Vacation
function deleteVacation(vacationId, userName) {
    appUI.fire({
        title: t.deleteAbsence,
        html: `<p>${t.confirmDeleteText} <strong>${userName}</strong> ${t.willBeDeleted}</p>`,
        icon: 'warning',
        showCancelButton: true,
        customClass: {
            confirmButton: 'swal-btn-gradient-red',
            cancelButton: 'swal-btn-gradient-gray',
            popup: 'swal-popup-rounded'
        },
        buttonsStyling: false,
        confirmButtonText: t.yes,
        cancelButtonText: t.no,
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            appUI.fire({
                title: t.deletingAbsence,
                allowOutsideClick: false,
                allowEscapeKey: false,
                didOpen: () => {
                    appUI.showLoading();
                }
            });
            
            fetch(`/${langCode}/absence/${vacationId}/delete/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    appUI.fire({
                        icon: 'success',
                        title: t.success,
                        text: t.absenceDeleted,
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
                        title: t.error,
                        text: data.message || t.absenceDeleteFailed,
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
                    title: t.error,
                    text: t.absenceDeleteFailed,
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
function generateVacationPDF(userId, dateFrom, dateTo, timeFrom, timeTo) {
    const langCode = window.location.pathname.split('/')[1];
    const url = `/${langCode}/absence/generate-pdf/`;
    
    // Create form data
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('date_from', dateFrom);
    formData.append('date_to', dateTo);
    if (timeFrom && timeFrom !== 'None') {
        formData.append('time_from', timeFrom);
    }
    if (timeTo && timeTo !== 'None') {
        formData.append('time_to', timeTo);
    }
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('Failed to generate PDF');
    })
    .then(blob => {
        // Create a URL for the blob
        const url = window.URL.createObjectURL(blob);
        // Open in new window
        window.open(url, '_blank');
        // Clean up
        setTimeout(() => window.URL.revokeObjectURL(url), 100);
    })
    .catch(error => {
        console.error('Error:', error);
        appUI.fire({
            icon: 'error',
            title: t.error,
            text: 'Failed to generate PDF',
            customClass: {
                confirmButton: 'swal-btn-gradient-gray',
                popup: 'swal-popup-rounded'
            },
            buttonsStyling: false
        });
    });
}

function approveVacation(vacationId, userName) {
    appUI.fire({
        title: t.approveAbsence,
        html: `<p>${t.confirmApproveText} <strong>${userName}</strong>?</p>`,
        icon: 'question',
        showCancelButton: true,
        customClass: {
            confirmButton: 'swal-btn-gradient-green',
            cancelButton: 'swal-btn-gradient-gray',
            popup: 'swal-popup-rounded'
        },
        buttonsStyling: false,
        confirmButtonText: t.yesApprove,
        cancelButtonText: t.no,
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            appUI.fire({
                title: t.approvingAbsence,
                allowOutsideClick: false,
                allowEscapeKey: false,
                didOpen: () => {
                    appUI.showLoading();
                }
            });
            
            fetch(`/${langCode}/absence/${vacationId}/approve/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    appUI.fire({
                        icon: 'success',
                        title: t.success,
                        text: t.absenceApproved,
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
                        title: t.error,
                        text: data.message || t.absenceApproveFailed,
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
                    title: t.error,
                    text: t.absenceApproveFailed,
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
