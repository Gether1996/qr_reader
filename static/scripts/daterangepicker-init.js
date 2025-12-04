// Initialize date range picker - supports multiple instances
function initDateRangePicker(suffix) {
    suffix = suffix || 'main';
    
    var dateFromId = '#date_from-' + suffix;
    var dateToId = '#date_to-' + suffix;
    var dateRangePickerId = '#dateRangePicker-' + suffix;
    var filterFormId = 'filterForm-' + suffix;
    
    // Check if element exists
    if (!$(dateRangePickerId).length) {
        console.log('DateRangePicker element not found for suffix:', suffix);
        return;
    }
    
    console.log('Initializing daterangepicker for:', suffix);
    
    var dateFrom = $(dateFromId).val();
    var dateTo = $(dateToId).val();
    
    var startDate = dateFrom ? moment(dateFrom, 'YYYY-MM-DD') : null;
    var endDate = dateTo ? moment(dateTo, 'YYYY-MM-DD') : null;
    
    // Get current language code
    var locale = daterangepickerLocale[currentLanguage];
    
    // Set initial display value
    if (startDate && endDate && startDate.isValid() && endDate.isValid()) {
        $(dateRangePickerId).val(startDate.format('DD.MM.YYYY') + ' - ' + endDate.format('DD.MM.YYYY'));
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
    
    // Remove existing event handlers
    $(dateRangePickerId).off('apply.daterangepicker cancel.daterangepicker');
    
    // Initialize daterangepicker
    $(dateRangePickerId).daterangepicker(pickerConfig);
    
    console.log('Daterangepicker initialized for:', suffix);
    
    $(dateRangePickerId).on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('DD.MM.YYYY') + ' - ' + picker.endDate.format('DD.MM.YYYY'));
        $(dateFromId).val(picker.startDate.format('YYYY-MM-DD'));
        $(dateToId).val(picker.endDate.format('YYYY-MM-DD'));
        document.getElementById(filterFormId).submit();
    });
    
    $(dateRangePickerId).on('cancel.daterangepicker', function(ev, picker) {
        $(this).val('');
        $(dateFromId).val('');
        $(dateToId).val('');
    });
}

// Initialize all date range pickers on page load
$(function() {
    console.log('Starting daterangepicker initialization...');
    
    // Find all dateRangePicker inputs on the page
    $('[id^="dateRangePicker-"]').each(function() {
        var $input = $(this);
        var inputId = $input.attr('id');
        var suffix = inputId.replace('dateRangePicker-', '');
        console.log('Found dateRangePicker input:', inputId, 'suffix:', suffix);
        
        // Only initialize if visible or if it's in a tab that's currently active
        var $tabPane = $input.closest('.tab-pane');
        if ($tabPane.length === 0 || $tabPane.hasClass('active')) {
            console.log('Initializing immediately (visible):', suffix);
            initDateRangePicker(suffix);
        } else {
            console.log('Skipping hidden tab element:', suffix);
        }
    });
    
    // Re-initialize daterangepicker when tabs are shown (for Bootstrap tabs)
    $('button[data-bs-toggle="tab"]').on('shown.bs.tab', function (e) {
        console.log('Tab shown event triggered');
        const targetTab = $(e.target).attr('data-bs-target');
        console.log('Target tab:', targetTab);
        
        // Small delay to ensure tab is fully visible
        setTimeout(function() {
            // Find dateRangePicker in the shown tab
            $(targetTab).find('[id^="dateRangePicker-"]').each(function() {
                var $input = $(this);
                var inputId = $input.attr('id');
                var suffix = inputId.replace('dateRangePicker-', '');
                console.log('Re-initializing dateRangePicker in tab:', suffix, 'element:', $input[0]);
                
                // Destroy existing instance if any
                if ($input.data('daterangepicker')) {
                    console.log('Removing existing daterangepicker instance');
                    $input.data('daterangepicker').remove();
                }
                
                // Initialize
                initDateRangePicker(suffix);
            });
        }, 100);
    });
});
