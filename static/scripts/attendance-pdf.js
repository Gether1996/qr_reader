// Attendance PDF generation functionality

// Translations for PDF generation
const pdfTranslations = {
    sk: {
        selectDateRange: 'Vyberte obdobie pre PDF report',
        dateRange: 'Obdobie',
        selectDates: 'Vyberte dátumy',
        cancel: 'Zrušiť',
        generate: 'Generovať PDF',
        fillAllFields: 'Vyberte dátumové obdobie',
        invalidDateRange: 'Neplatné obdobie - dátum ukončenia musí byť po dátume začiatku'
    },
    en: {
        selectDateRange: 'Select date range for PDF report',
        dateRange: 'Date Range',
        selectDates: 'Select dates',
        cancel: 'Cancel',
        generate: 'Generate PDF',
        fillAllFields: 'Please select a date range',
        invalidDateRange: 'Invalid date range - end date must be after start date'
    },
    es: {
        selectDateRange: 'Seleccione el período para el informe PDF',
        dateRange: 'Período',
        selectDates: 'Seleccionar fechas',
        cancel: 'Cancelar',
        generate: 'Generar PDF',
        fillAllFields: 'Seleccione un rango de fechas',
        invalidDateRange: 'Rango de fechas no válido - la fecha de fin debe ser posterior a la fecha de inicio'
    },
    de: {
        selectDateRange: 'Wählen Sie den Zeitraum für den PDF-Bericht',
        dateRange: 'Zeitraum',
        selectDates: 'Daten auswählen',
        cancel: 'Abbrechen',
        generate: 'PDF generieren',
        fillAllFields: 'Bitte wählen Sie einen Datumsbereich',
        invalidDateRange: 'Ungültiger Datumsbereich - Enddatum muss nach Startdatum liegen'
    }
};

const pdfT = pdfTranslations[langCode] || pdfTranslations.en;

// Initialize daterangepicker for PDF modal (uses global daterangepickerLocale from base.html)
function initPDFDateRangePicker(inputId, callback) {
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

function generateAttendancePDF(userId, buttonElement) {
    // Create a temporary hidden input for daterangepicker
    const tempInput = document.createElement('input');
    tempInput.type = 'text';
    tempInput.id = 'temp-pdf-daterange';
    tempInput.style.position = 'absolute';
    tempInput.style.opacity = '0';
    tempInput.style.pointerEvents = 'none';
    document.body.appendChild(tempInput);
    
    const locale = daterangepickerLocale[langCode] || daterangepickerLocale.sk;
    
    // Check if mobile
    const isMobile = window.innerWidth <= 768;
    
    // Initialize daterangepicker directly on the button or near it
    $(tempInput).daterangepicker({
        locale: {
            cancelLabel: locale.cancelLabel,
            applyLabel: locale.applyLabel,
            customRangeLabel: locale.customRangeLabel,
            daysOfWeek: locale.daysOfWeek,
            monthNames: locale.monthNames,
            firstDay: locale.firstDay,
            format: locale.format,
        },
        ranges: locale.ranges,
        autoUpdateInput: false,
        opens: isMobile ? 'center' : 'left',
        drops: 'down',
        alwaysShowCalendars: true,
        parentEl: 'body'
    });
    
    // Show the daterangepicker immediately
    $(tempInput).data('daterangepicker').show();
    
    // Position and lock the picker for desktop
    if (buttonElement && !isMobile) {
        const rect = buttonElement.getBoundingClientRect();
        const picker = $(tempInput).data('daterangepicker').container[0];
        const pickerWidth = 640;
        const pickerHeight = 350;
        
        // Calculate vertical position
        let top = rect.bottom + 5;
        if (top + pickerHeight > window.innerHeight) {
            top = rect.top - pickerHeight - 5;
            if (top < 0) {
                top = 10;
            }
        }
        
        // Calculate horizontal position
        let left = rect.right - pickerWidth;
        if (left < 10) {
            left = 10;
        }
        if (left + pickerWidth > window.innerWidth - 10) {
            left = window.innerWidth - pickerWidth - 10;
        }
        
        // Set position
        picker.style.position = 'fixed';
        picker.style.zIndex = '9999';
        picker.style.top = top + 'px';
        picker.style.left = left + 'px';
        
        // Lock position with MutationObserver to prevent daterangepicker from changing it
        const observer = new MutationObserver(() => {
            if (picker.style.position !== 'fixed' || 
                picker.style.top !== top + 'px' || 
                picker.style.left !== left + 'px') {
                picker.style.position = 'fixed';
                picker.style.top = top + 'px';
                picker.style.left = left + 'px';
            }
        });
        
        observer.observe(picker, { 
            attributes: true, 
            attributeFilter: ['style'] 
        });
        
        // Clean up observer when picker is hidden
        $(tempInput).on('hide.daterangepicker', () => {
            observer.disconnect();
        });
    }
    
    // Handle date selection
    $(tempInput).on('apply.daterangepicker', function(ev, picker) {
        const startDate = picker.startDate.format('YYYY-MM-DD');
        const endDate = picker.endDate.format('YYYY-MM-DD');
        
        // Build URL with selected dates
        const url = `/${langCode}/company/user/${userId}/attendance-pdf/?date_from=${encodeURIComponent(startDate)}&date_to=${encodeURIComponent(endDate)}`;
        
        // Open PDF in new tab
        window.open(url, '_blank');
        
        // Cleanup
        $(tempInput).data('daterangepicker').remove();
        tempInput.remove();
    });
    
    // Handle cancel
    $(tempInput).on('cancel.daterangepicker', function(ev, picker) {
        // Cleanup
        $(tempInput).data('daterangepicker').remove();
        tempInput.remove();
    });
    
    // Cleanup on outside click
    $(tempInput).on('hide.daterangepicker', function(ev, picker) {
        setTimeout(() => {
            if (tempInput.parentNode) {
                $(tempInput).data('daterangepicker').remove();
                tempInput.remove();
            }
        }, 100);
    });
}

function generateAttendanceExcel(userId, buttonElement) {
    // Create a temporary hidden input for daterangepicker
    const tempInput = document.createElement('input');
    tempInput.type = 'text';
    tempInput.id = 'temp-excel-daterange';
    tempInput.style.position = 'absolute';
    tempInput.style.opacity = '0';
    tempInput.style.pointerEvents = 'none';
    document.body.appendChild(tempInput);
    
    const locale = daterangepickerLocale[langCode] || daterangepickerLocale.sk;
    
    // Check if mobile
    const isMobile = window.innerWidth <= 768;
    
    // Initialize daterangepicker directly on the button or near it
    $(tempInput).daterangepicker({
        locale: {
            cancelLabel: locale.cancelLabel,
            applyLabel: locale.applyLabel,
            customRangeLabel: locale.customRangeLabel,
            daysOfWeek: locale.daysOfWeek,
            monthNames: locale.monthNames,
            firstDay: locale.firstDay,
            format: locale.format,
        },
        ranges: locale.ranges,
        autoUpdateInput: false,
        opens: isMobile ? 'center' : 'left',
        drops: 'down',
        alwaysShowCalendars: true,
        parentEl: 'body'
    });
    
    // Show the daterangepicker immediately
    $(tempInput).data('daterangepicker').show();
    
    // Position and lock the picker for desktop
    if (buttonElement && !isMobile) {
        const rect = buttonElement.getBoundingClientRect();
        const picker = $(tempInput).data('daterangepicker').container[0];
        const pickerWidth = 640;
        const pickerHeight = 350;
        
        // Calculate vertical position
        let top = rect.bottom + 5;
        if (top + pickerHeight > window.innerHeight) {
            top = rect.top - pickerHeight - 5;
            if (top < 0) {
                top = 10;
            }
        }
        
        // Calculate horizontal position
        let left = rect.right - pickerWidth;
        if (left < 10) {
            left = 10;
        }
        if (left + pickerWidth > window.innerWidth - 10) {
            left = window.innerWidth - pickerWidth - 10;
        }
        
        // Set position
        picker.style.position = 'fixed';
        picker.style.zIndex = '9999';
        picker.style.top = top + 'px';
        picker.style.left = left + 'px';
        
        // Lock position with MutationObserver to prevent daterangepicker from changing it
        const observer = new MutationObserver(() => {
            if (picker.style.position !== 'fixed' || 
                picker.style.top !== top + 'px' || 
                picker.style.left !== left + 'px') {
                picker.style.position = 'fixed';
                picker.style.top = top + 'px';
                picker.style.left = left + 'px';
            }
        });
        
        observer.observe(picker, { 
            attributes: true, 
            attributeFilter: ['style'] 
        });
        
        // Clean up observer when picker is hidden
        $(tempInput).on('hide.daterangepicker', () => {
            observer.disconnect();
        });
    }
    
    // Handle date selection
    $(tempInput).on('apply.daterangepicker', function(ev, picker) {
        const startDate = picker.startDate.format('YYYY-MM-DD');
        const endDate = picker.endDate.format('YYYY-MM-DD');
        
        // Build URL with selected dates
        const url = `/${langCode}/company/user/${userId}/attendance-excel/?date_from=${encodeURIComponent(startDate)}&date_to=${encodeURIComponent(endDate)}`;
        
        // Open Excel download in new tab
        window.open(url, '_blank');
        
        // Cleanup
        $(tempInput).data('daterangepicker').remove();
        tempInput.remove();
    });
    
    // Handle cancel
    $(tempInput).on('cancel.daterangepicker', function(ev, picker) {
        // Cleanup
        $(tempInput).data('daterangepicker').remove();
        tempInput.remove();
    });
    
    // Cleanup on outside click
    $(tempInput).on('hide.daterangepicker', function(ev, picker) {
        setTimeout(() => {
            if (tempInput.parentNode) {
                $(tempInput).data('daterangepicker').remove();
                tempInput.remove();
            }
        }, 100);
    });
}
