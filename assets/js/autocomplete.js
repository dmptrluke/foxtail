import TomSelect from 'tom-select';
import 'tom-select/dist/css/tom-select.bootstrap5.css';

export function initAutocomplete() {
    document.querySelectorAll('[data-autocomplete-url]').forEach(el => {
        if (el.tomselect) return;
        new TomSelect(el, {
            valueField: 'id',
            labelField: 'text',
            searchField: 'text',
            load(query, callback) {
                fetch(`${el.dataset.autocompleteUrl}?q=${encodeURIComponent(query)}`)
                    .then(r => r.json())
                    .then(data => callback(data.results))
                    .catch(() => callback());
            }
        });
    });
}
