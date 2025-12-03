// Initialize date range picker
$(function() {
    var dateFrom = $('#date_from').val();
    var dateTo = $('#date_to').val();
    
    var startDate = dateFrom ? moment(dateFrom, 'YYYY-MM-DD') : null;
    var endDate = dateTo ? moment(dateTo, 'YYYY-MM-DD') : null;
    
    // Get current language code
    var locale = daterangepickerLocale[currentLanguage];
    
    // Set initial display value
    if (startDate && endDate && startDate.isValid() && endDate.isValid()) {
        $('#dateRangePicker').val(startDate.format('DD.MM.YYYY') + ' - ' + endDate.format('DD.MM.YYYY'));
    }
    
    // Check if mobile device
    var isMobile = window.innerWidth <= 768;
    
    var pickerConfig = {
        autoUpdateInput: false,
        timePicker: false,
        timePicker24Hour: false,
        showDropdowns: true,
        opens: isMobile ? 'center' : 'center',
        drops: isMobile ? 'down' : 'auto',
        alwaysShowCalendars: true,
        locale: {
            cancelLabel: locale.cancelLabel,
            applyLabel: locale.applyLabel,
            customRangeLabel: locale.customRangeLabel,
            daysOfWeek: locale.daysOfWeek,
            monthNames: locale.monthNames,
            firstDay: locale.firstDay,
            format: locale.format
        },
        ranges: locale.ranges
    };
    
    if (startDate && endDate && startDate.isValid() && endDate.isValid()) {
        pickerConfig.startDate = startDate;
        pickerConfig.endDate = endDate;
    }
    
    $('#dateRangePicker').daterangepicker(pickerConfig);
    
    $('#dateRangePicker').on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('DD.MM.YYYY') + ' - ' + picker.endDate.format('DD.MM.YYYY'));
        $('#date_from').val(picker.startDate.format('YYYY-MM-DD'));
        $('#date_to').val(picker.endDate.format('YYYY-MM-DD'));
        document.getElementById('filterForm').submit();
    });
    
    $('#dateRangePicker').on('cancel.daterangepicker', function(ev, picker) {
        $(this).val('');
        $('#date_from').val('');
        $('#date_to').val('');
    });
});
