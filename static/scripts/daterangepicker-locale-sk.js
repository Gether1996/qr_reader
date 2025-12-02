// Slovak locale for daterangepicker
var daterangepickerLocale = {
    sk: {
        cancelLabel: 'Vymazať',
        applyLabel: 'Použiť',
        customRangeLabel: 'Vlastný rozsah',
        daysOfWeek: ['Ne', 'Po', 'Ut', 'St', 'Št', 'Pi', 'So'],
        monthNames: [
            'Január', 'Február', 'Marec', 'Apríl', 'Máj', 'Jún',
            'Júl', 'August', 'September', 'Október', 'November', 'December'
        ],
        firstDay: 1,
        format: 'DD.MM.YYYY',
        timePicker: false,
        ranges: {
            'Dnes': [moment().startOf('day'), moment().endOf('day')],
            'Včera': [moment().subtract(1, 'days').startOf('day'), moment().subtract(1, 'days').endOf('day')],
            'Posledných 7 dní': [moment().subtract(6, 'days').startOf('day'), moment().endOf('day')],
            'Posledných 30 dní': [moment().subtract(29, 'days').startOf('day'), moment().endOf('day')],
            'Tento mesiac': [moment().startOf('month'), moment().endOf('month')],
            'Minulý mesiac': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        }
    }
};
