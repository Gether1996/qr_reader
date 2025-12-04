// Translations
const vacationTranslations = {
    sk: {
        addAbsence: 'Pridať neprítomnosť',
        editAbsence: 'Upraviť neprítomnosť',
        deleteAbsence: 'Vymazať neprítomnosť',
        selectEmployee: 'Vyberte zamestnanca',
        employee: 'Zamestnanec',
        dateRange: 'Obdobie',
        from: 'Od',
        to: 'Do',
        cancel: 'Zrušiť',
        save: 'Uložiť',
        delete: 'Vymazať',
        confirmDelete: 'Naozaj chcete vymazať túto neprítomnosť?',
        confirmDeleteText: 'Neprítomnosť pre zamestnanca',
        willBeDeleted: 'bude vymazaná',
        yes: 'Áno, vymazať',
        no: 'Nie',
        success: 'Úspech',
        error: 'Chyba',
        absenceAdded: 'Neprítomnosť bola úspešne pridaná',
        absenceUpdated: 'Neprítomnosť bola úspešne aktualizovaná',
        absenceDeleted: 'Neprítomnosť bola úspešne vymazaná',
        absenceAddFailed: 'Nepodarilo sa pridať neprítomnosť',
        absenceUpdateFailed: 'Nepodarilo sa aktualizovať neprítomnosť',
        absenceDeleteFailed: 'Nepodarilo sa vymazať neprítomnosť',
        fillAllFields: 'Vyplňte všetky polia vrátane typu',
        invalidDateRange: 'Neplatné obdobie - dátum ukončenia musí byť po dátume začiatku',
        selectDates: 'Vyberte dátumy',
        type: 'Typ',
        vacation: 'Dovolenka',
        sickLeave: 'PN (Pracovná neschopnosť)',
        selectType: 'Vyberte typ'
    },
    en: {
        addAbsence: 'Add Absence',
        editAbsence: 'Edit Absence',
        deleteAbsence: 'Delete Absence',
        selectEmployee: 'Select employee',
        employee: 'Employee',
        dateRange: 'Period',
        from: 'From',
        to: 'To',
        cancel: 'Cancel',
        save: 'Save',
        delete: 'Delete',
        confirmDelete: 'Are you sure you want to delete this absence?',
        confirmDeleteText: 'Absence for employee',
        willBeDeleted: 'will be deleted',
        yes: 'Yes, delete',
        no: 'No',
        success: 'Success',
        error: 'Error',
        absenceAdded: 'Absence successfully added',
        absenceUpdated: 'Absence successfully updated',
        absenceDeleted: 'Absence successfully deleted',
        absenceAddFailed: 'Failed to add absence',
        absenceUpdateFailed: 'Failed to update absence',
        absenceDeleteFailed: 'Failed to delete absence',
        fillAllFields: 'Please fill all fields including type',
        invalidDateRange: 'Invalid date range - end date must be after start date',
        selectDates: 'Select dates',
        type: 'Type',
        vacation: 'Vacation',
        sickLeave: 'Sick Leave',
        selectType: 'Select type'
    },
    es: {
        addAbsence: 'Agregar Ausencia',
        editAbsence: 'Editar Ausencia',
        deleteAbsence: 'Eliminar Ausencia',
        selectEmployee: 'Seleccionar empleado',
        employee: 'Empleado',
        dateRange: 'Período',
        from: 'Desde',
        to: 'Hasta',
        cancel: 'Cancelar',
        save: 'Guardar',
        delete: 'Eliminar',
        confirmDelete: '¿Está seguro de que desea eliminar esta ausencia?',
        confirmDeleteText: 'Ausencia para el empleado',
        willBeDeleted: 'será eliminada',
        yes: 'Sí, eliminar',
        no: 'No',
        success: 'Éxito',
        error: 'Error',
        absenceAdded: 'Ausencia agregada exitosamente',
        absenceUpdated: 'Ausencia actualizada exitosamente',
        absenceDeleted: 'Ausencia eliminada exitosamente',
        absenceAddFailed: 'No se pudo agregar la ausencia',
        absenceUpdateFailed: 'No se pudo actualizar la ausencia',
        absenceDeleteFailed: 'No se pudo eliminar la ausencia',
        fillAllFields: 'Por favor complete todos los campos incluyendo el tipo',
        invalidDateRange: 'Rango de fechas no válido - la fecha de fin debe ser posterior a la fecha de inicio',
        selectDates: 'Seleccionar fechas',
        type: 'Tipo',
        vacation: 'Vacaciones',
        sickLeave: 'Baja por enfermedad',
        selectType: 'Seleccionar tipo'
    },
    de: {
        addAbsence: 'Abwesenheit hinzufügen',
        editAbsence: 'Abwesenheit bearbeiten',
        deleteAbsence: 'Abwesenheit löschen',
        selectEmployee: 'Mitarbeiter auswählen',
        employee: 'Mitarbeiter',
        dateRange: 'Zeitraum',
        from: 'Von',
        to: 'Bis',
        cancel: 'Abbrechen',
        save: 'Speichern',
        delete: 'Löschen',
        confirmDelete: 'Möchten Sie diese Abwesenheit wirklich löschen?',
        confirmDeleteText: 'Abwesenheit für Mitarbeiter',
        willBeDeleted: 'wird gelöscht',
        yes: 'Ja, löschen',
        no: 'Nein',
        success: 'Erfolg',
        error: 'Fehler',
        absenceAdded: 'Abwesenheit erfolgreich hinzugefügt',
        absenceUpdated: 'Abwesenheit erfolgreich aktualisiert',
        absenceDeleted: 'Abwesenheit erfolgreich gelöscht',
        absenceAddFailed: 'Abwesenheit konnte nicht hinzugefügt werden',
        absenceUpdateFailed: 'Abwesenheit konnte nicht aktualisiert werden',
        absenceDeleteFailed: 'Abwesenheit konnte nicht gelöscht werden',
        fillAllFields: 'Bitte füllen Sie alle Felder einschließlich Typ aus',
        invalidDateRange: 'Ungültiger Datumsbereich - Enddatum muss nach Startdatum liegen',
        selectDates: 'Daten auswählen',
        type: 'Typ',
        vacation: 'Urlaub',
        sickLeave: 'Krankschreibung',
        selectType: 'Typ auswählen'
    }
};

const t = vacationTranslations[langCode] || vacationTranslations.en;

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

    Swal.fire({
        title: t.addLeave,
        html: `
            <div class="container-fluid px-0">
                <div class="row g-3">
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-2">${t.employee}</label>
                        <select id="swal-employee" class="form-select form-select-lg">
                            ${employeeOptions}
                        </select>
                    </div>
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-2">${t.type}</label>
                        <select id="swal-type" class="form-select form-select-lg">
                            <option value="">${t.selectType}</option>
                            <option value="vacation">${t.vacation}</option>
                            <option value="sick_leave">${t.sickLeave}</option>
                        </select>
                    </div>
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-2">${t.dateRange}</label>
                        <input type="text" id="swal-daterange" class="form-control form-control-lg" readonly placeholder="${t.selectDates}" style="cursor: pointer; background-color: white;">
                    </div>
                </div>
            </div>
        `,
        width: '600px',
        showCancelButton: true,
        confirmButtonText: t.save,
        cancelButtonText: t.cancel,
        customClass: {
            confirmButton: 'swal-btn-gradient-green',
            cancelButton: 'swal-btn-gradient-gray',
            popup: 'swal-popup-rounded'
        },
        buttonsStyling: false,
        didOpen: () => {
            initModalDateRangePicker('swal-daterange', (start, end) => {
                startDate = start.format('YYYY-MM-DD');
                endDate = end.format('YYYY-MM-DD');
            });
        },
        preConfirm: () => {
            selectedUserId = document.getElementById('swal-employee').value;
            const selectedType = document.getElementById('swal-type').value;
            
            if (!selectedUserId || !selectedType || !startDate || !endDate) {
                Swal.showValidationMessage(t.fillAllFields);
                return false;
            }

            if (new Date(endDate) < new Date(startDate)) {
                Swal.showValidationMessage(t.invalidDateRange);
                return false;
            }

            return { userId: selectedUserId, dateFrom: startDate, dateTo: endDate, type: selectedType };
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const data = result.value;
            
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
                    type: data.type
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    Swal.fire({
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
                    Swal.fire({
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
                Swal.fire({
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
function editVacation(vacationId, currentUserId, currentUserName, currentDateFrom, currentDateTo, currentType, users) {
    let selectedUserId = currentUserId;
    let startDate = currentDateFrom;
    let endDate = currentDateTo;

    // Create employee select options
    let employeeOptions = '';
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

    Swal.fire({
        title: t.editLeave,
        html: `
            <div class="container-fluid px-0">
                <div class="row g-3">
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-2">${t.employee}</label>
                        <select id="swal-employee" class="form-select form-select-lg">
                            ${employeeOptions}
                        </select>
                    </div>
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-2">${t.type}</label>
                        <select id="swal-type" class="form-select form-select-lg">
                            <option value="">${t.selectType}</option>
                            <option value="vacation" ${currentType === 'vacation' ? 'selected' : ''}>${t.vacation}</option>
                            <option value="sick_leave" ${currentType === 'sick_leave' ? 'selected' : ''}>${t.sickLeave}</option>
                        </select>
                    </div>
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-2">${t.dateRange}</label>
                        <input type="text" id="swal-daterange" class="form-control form-control-lg" readonly placeholder="${t.selectDates}" value="${displayRange}" style="cursor: pointer; background-color: white;">
                    </div>
                </div>
            </div>
        `,
        width: '600px',
        showCancelButton: true,
        confirmButtonText: t.save,
        cancelButtonText: t.cancel,
        customClass: {
            confirmButton: 'swal-btn-gradient-blue',
            cancelButton: 'swal-btn-gradient-gray',
            popup: 'swal-popup-rounded'
        },
        buttonsStyling: false,
        didOpen: () => {
            initModalDateRangePicker('swal-daterange', (start, end) => {
                startDate = start.format('YYYY-MM-DD');
                endDate = end.format('YYYY-MM-DD');
            });
        },
        preConfirm: () => {
            selectedUserId = document.getElementById('swal-employee').value;
            const selectedType = document.getElementById('swal-type').value;
            
            if (!selectedUserId || !selectedType || !startDate || !endDate) {
                Swal.showValidationMessage(t.fillAllFields);
                return false;
            }

            if (new Date(endDate) < new Date(startDate)) {
                Swal.showValidationMessage(t.invalidDateRange);
                return false;
            }

            return { userId: selectedUserId, dateFrom: startDate, dateTo: endDate, type: selectedType };
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const data = result.value;
            
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
                    type: data.type
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    Swal.fire({
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
                    Swal.fire({
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
                Swal.fire({
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

    Swal.fire({
        title: t.addLeave,
        html: `
            <div class="container-fluid px-0">
                <div class="row g-3">
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-2">${t.employee}</label>
                        <input type="text" class="form-control form-control-lg" value="${userName}" readonly disabled>
                    </div>
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-2">${t.type}</label>
                        <select id="swal-type" class="form-select form-select-lg">
                            <option value="">${t.selectType}</option>
                            <option value="vacation">${t.vacation}</option>
                            <option value="sick_leave">${t.sickLeave}</option>
                        </select>
                    </div>
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-2">${t.dateRange}</label>
                        <input type="text" id="swal-daterange" class="form-control form-control-lg" readonly placeholder="${t.selectDates}" style="cursor: pointer; background-color: white;">
                    </div>
                </div>
            </div>
        `,
        width: '600px',
        showCancelButton: true,
        confirmButtonText: t.save,
        cancelButtonText: t.cancel,
        customClass: {
            confirmButton: 'swal-btn-gradient-green',
            cancelButton: 'swal-btn-gradient-gray',
            popup: 'swal-popup-rounded'
        },
        buttonsStyling: false,
        didOpen: () => {
            initModalDateRangePicker('swal-daterange', (start, end) => {
                startDate = start.format('YYYY-MM-DD');
                endDate = end.format('YYYY-MM-DD');
            });
        },
        preConfirm: () => {
            const selectedType = document.getElementById('swal-type').value;
            
            if (!selectedType || !startDate || !endDate) {
                Swal.showValidationMessage(t.fillAllFields);
                return false;
            }

            if (new Date(endDate) < new Date(startDate)) {
                Swal.showValidationMessage(t.invalidDateRange);
                return false;
            }

            return { userId: userId, dateFrom: startDate, dateTo: endDate, type: selectedType };
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const data = result.value;
            
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
                    type: data.type
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    Swal.fire({
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
                    Swal.fire({
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
                Swal.fire({
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
function editVacationSimple(vacationId, userId, userName, currentDateFrom, currentDateTo, currentType) {
    let startDate = currentDateFrom;
    let endDate = currentDateTo;

    // Format dates for display
    const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('sk-SK');
    };

    const displayRange = `${formatDate(currentDateFrom)} - ${formatDate(currentDateTo)}`;

    Swal.fire({
        title: t.editLeave,
        html: `
            <div class="container-fluid px-0">
                <div class="row g-3">
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-2">${t.employee}</label>
                        <input type="text" class="form-control form-control-lg" value="${userName}" readonly disabled>
                    </div>
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-2">${t.type}</label>
                        <select id="swal-type" class="form-select form-select-lg">
                            <option value="">${t.selectType}</option>
                            <option value="vacation" ${currentType === 'vacation' ? 'selected' : ''}>${t.vacation}</option>
                            <option value="sick_leave" ${currentType === 'sick_leave' ? 'selected' : ''}>${t.sickLeave}</option>
                        </select>
                    </div>
                    <div class="col-12">
                        <label class="form-label fw-semibold mb-2">${t.dateRange}</label>
                        <input type="text" id="swal-daterange" class="form-control form-control-lg" readonly placeholder="${t.selectDates}" value="${displayRange}" style="cursor: pointer; background-color: white;">
                    </div>
                </div>
            </div>
        `,
        width: '600px',
        showCancelButton: true,
        confirmButtonText: t.save,
        cancelButtonText: t.cancel,
        customClass: {
            confirmButton: 'swal-btn-gradient-blue',
            cancelButton: 'swal-btn-gradient-gray',
            popup: 'swal-popup-rounded'
        },
        buttonsStyling: false,
        didOpen: () => {
            initModalDateRangePicker('swal-daterange', (start, end) => {
                startDate = start.format('YYYY-MM-DD');
                endDate = end.format('YYYY-MM-DD');
            });
        },
        preConfirm: () => {
            const selectedType = document.getElementById('swal-type').value;
            
            if (!selectedType || !startDate || !endDate) {
                Swal.showValidationMessage(t.fillAllFields);
                return false;
            }

            if (new Date(endDate) < new Date(startDate)) {
                Swal.showValidationMessage(t.invalidDateRange);
                return false;
            }

            return { userId: userId, dateFrom: startDate, dateTo: endDate, type: selectedType };
        }
    }).then((result) => {
        if (result.isConfirmed) {
            const data = result.value;
            
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
                    type: data.type
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    Swal.fire({
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
                    Swal.fire({
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
                Swal.fire({
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
    Swal.fire({
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
                    Swal.fire({
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
                    Swal.fire({
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
                Swal.fire({
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
