import 'core-js/stable';
import 'regenerator-runtime/runtime';

import 'bootstrap';
import 'colcade';

function on_load() {
    $('[data-toggle="tooltip"]').tooltip();

    $('#id_text').keyup(function () {
        let length = $(this).val().length;
        let limit = $(this).attr('maxlength');

        length = limit - length;
        let plural = (length === 1) ? "" : "s";
        $('#hint_id_text').text(length + ' character' + plural + ' remaining.');
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', on_load);
} else {
    on_load();
}
