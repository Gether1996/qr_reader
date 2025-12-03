// Attendance PDF generation functionality

function generateAttendancePDF(userId) {
    const dateRangeInput = document.getElementById('dateRangePicker');
    const dateFromInput = document.getElementById('date_from');
    const dateToInput = document.getElementById('date_to');
    
    if (!dateFromInput || !dateToInput || !dateFromInput.value || !dateToInput.value) {
        if (dateRangeInput) {
            dateRangeInput.style.borderColor = '#dc3545';
            dateRangeInput.style.backgroundColor = '#ffe6e6';
            
            // Reset color after 3 seconds
            setTimeout(() => {
                dateRangeInput.style.borderColor = '';
                dateRangeInput.style.backgroundColor = '';
            }, 3000);
        }
        showError(translations.error, translations.selectDateRange || 'Please select a date range first!');
        return;
    }
    
    const langCode = window.location.pathname.split('/')[1];
    const dateFrom = dateFromInput.value;
    const dateTo = dateToInput.value;
    
    // Build URL with current filters
    const url = `/${langCode}/company/user/${userId}/attendance-pdf/?date_from=${encodeURIComponent(dateFrom)}&date_to=${encodeURIComponent(dateTo)}`;
    
    // Open PDF in new tab
    window.open(url, '_blank');
}
