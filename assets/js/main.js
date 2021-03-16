import Dropdown from 'bootstrap/js/dist/dropdown';
import Collapse from 'bootstrap/js/dist/collapse';
import Alert from 'bootstrap/js/dist/alert';
import Popover from 'bootstrap/js/dist/popover';
import Tooltip from 'bootstrap/js/dist/tooltip';

import 'colcade';

function on_load() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new Tooltip(tooltipTriggerEl)
    })

    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
      return new Popover(popoverTriggerEl)
    })

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
