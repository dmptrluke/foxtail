import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/400-italic.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
import '../scss/index.scss';

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

    const textInput = document.getElementById('id_text');
    if (textInput) {
        textInput.addEventListener('keyup', function () {
            const remaining = this.maxLength - this.value.length;
            const plural = remaining === 1 ? '' : 's';
            document.getElementById('hint_id_text').textContent =
                remaining + ' character' + plural + ' remaining.';
        });
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', on_load);
} else {
    on_load();
}
