import TomSelect from 'tom-select';
import 'tom-select/dist/css/tom-select.bootstrap5.css';

function initTagAutocomplete(el) {
    const initial = el.value ? el.value.split(',').map(s => s.trim()).filter(Boolean) : [];
    new TomSelect(el, {
        plugins: ['remove_button'],
        delimiter: ',',
        persist: false,
        create: true,
        valueField: 'text',
        labelField: 'text',
        searchField: 'text',
        options: initial.map(t => ({ text: t })),
        items: initial,
        load(query, callback) {
            fetch(`${el.dataset.autocompleteUrl}?q=${encodeURIComponent(query)}`)
                .then(r => r.json())
                .then(data => callback(data.results))
                .catch(() => callback());
        },
    });
}

function initSelectAutocomplete(el) {
    const isMultiple = el.multiple;
    const parent = document.getElementById(el.dataset.autocompleteParent);
    let generation = 0;
    // Clear Django's "---------" label; the option must remain for blank submissions
    const blank = el.querySelector('option[value=""]');
    if (blank) blank.textContent = '';
    const control = new TomSelect(el, {
        plugins: isMultiple ? ['remove_button'] : ['clear_button'],
        allowEmptyOption: false,
        valueField: 'id',
        labelField: 'text',
        searchField: 'text',
        load(query, callback) {
            const requestGeneration = generation;
            const parentValue = parent?.value;
            const url = new URL(el.dataset.autocompleteUrl, document.baseURI);
            url.searchParams.set('q', query);
            if (parent) url.searchParams.set(el.dataset.autocompleteParentParam, parentValue);
            fetch(url)
                .then(r => r.json())
                .then(data => callback(requestGeneration === generation && parentValue === parent?.value ? data.results : []))
                .catch(() => callback());
        },
    });
    if (parent) {
        parent.addEventListener('change', () => {
            generation++;
            control.clear();
            control.clearOptions();
            control.setTextboxValue('');
            if (parent.value) {
                control.enable();
                control.load('');
            } else {
                control.disable();
            }
        });
        if (parent.value) control.load('');
        else control.disable();
    }
}

export function initAutocomplete() {
    document.querySelectorAll('[data-autocomplete-url]').forEach(el => {
        if (el.tomselect) return;

        if (el.tagName === 'INPUT') {
            initTagAutocomplete(el);
        } else {
            initSelectAutocomplete(el);
        }
    });
}
