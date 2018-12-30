$(document).ready(function () {
    var updateAdminElems = function() {
        var editableContentElems = $('.smc-admin-editable-content');
        $.each(editableContentElems, function(index, elem) {
            elem = $(elem);
            var parentElem = elem.parent();

            elem.css('margin-top', parentElem.css('padding-top'));
            elem.css('margin-right', parentElem.css('padding-right'));
        });
    }
    $(window).on('resize', function(event) {
        updateAdminElems();
    });
    updateAdminElems();
});
