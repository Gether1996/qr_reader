// German locale for daterangepicker
if (typeof daterangepickerLocale === 'undefined') {
    var daterangepickerLocale = {};
}
daterangepickerLocale.de = {
        cancelLabel: 'Löschen',
        applyLabel: 'Anwenden',
        customRangeLabel: 'Benutzerdefiniert',
        daysOfWeek: ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'],
        monthNames: [
            'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
            'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
        ],
        firstDay: 1,
        format: 'DD.MM.YYYY',
        timePicker: false,
        ranges: {
            'Heute': [moment().startOf('day'), moment().endOf('day')],
            'Gestern': [moment().subtract(1, 'days').startOf('day'), moment().subtract(1, 'days').endOf('day')],
            'Letzte 7 Tage': [moment().subtract(6, 'days').startOf('day'), moment().endOf('day')],
            'Letzte 30 Tage': [moment().subtract(29, 'days').startOf('day'), moment().endOf('day')],
            'Dieser Monat': [moment().startOf('month'), moment().endOf('month')],
            'Letzter Monat': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        }
};
