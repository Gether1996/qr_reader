// Spanish locale for daterangepicker
var daterangepickerLocale = {
    es: {
        cancelLabel: 'Borrar',
        applyLabel: 'Aplicar',
        customRangeLabel: 'Rango personalizado',
        daysOfWeek: ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá'],
        monthNames: [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ],
        firstDay: 1,
        format: 'DD.MM.YYYY',
        timePicker: false,
        ranges: {
            'Hoy': [moment().startOf('day'), moment().endOf('day')],
            'Ayer': [moment().subtract(1, 'days').startOf('day'), moment().subtract(1, 'days').endOf('day')],
            'Últimos 7 días': [moment().subtract(6, 'days').startOf('day'), moment().endOf('day')],
            'Últimos 30 días': [moment().subtract(29, 'days').startOf('day'), moment().endOf('day')],
            'Este mes': [moment().startOf('month'), moment().endOf('month')],
            'Mes pasado': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        }
    }
};
