(function($) {
    $(document).on('formset:added', function(event, $row, formsetName) {
        $('fieldset.collapse.smc-expand-on-create', $row).removeClass('collapsed');
    });
})(django.jQuery);
