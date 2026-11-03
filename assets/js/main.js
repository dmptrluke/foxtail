import '../scss/index.scss';

import 'bootstrap/js/dist/dropdown';
import 'bootstrap/js/dist/collapse';
import 'bootstrap/js/dist/alert';

import 'colcade';
import htmx from 'htmx.org';
import { getCsrfToken } from './csrf.js';
import { initFooter } from './footer.js';

htmx.config.includeIndicatorStyles = false;
htmx.config.selfRequestsOnly = true;
htmx.config.allowScriptTags = false;
htmx.config.allowEval = false;
window.htmx = htmx;

document.addEventListener('htmx:configRequest', (e) => {
    const token = getCsrfToken();
    if (token) e.detail.headers['X-CSRFToken'] = token;
});

// --- Comment character counter ---

function initCharCounter() {
    const textInput = document.getElementById('id_text');
    const hint = document.getElementById('hint_id_text');
    if (!textInput || !hint) return;

    textInput.addEventListener('keyup', () => {
        const remaining = textInput.maxLength - textInput.value.length;
        const plural = remaining === 1 ? '' : 's';
        hint.textContent = `${remaining} character${plural} remaining.`;
    });
}

document.addEventListener('htmx:afterSwap', () => initCharCounter());

// --- Init ---

function onLoad() {
    initFooter();
    initCharCounter();
    if (document.getElementById('id_age_privacy')) {
        import('./profileEdit.js').then(m => m.initProfileEdit());
    }

    if (document.querySelector('[data-image-widget]')) {
        import('./imageWidget.js').then(m => m.initImageWidgets());
    }

    if (document.querySelector('[data-map]')) {
        import('./map.js').then(m => m.initMaps());
    }

    if (document.querySelector('[data-autocomplete-url]')) {
        import('./autocomplete.js').then(m => m.initAutocomplete());
    }

    if (document.querySelector('[data-interest-url]')) {
        import('./eventInterest.js').then(m => m.initEventInterest());
    }

    if (document.querySelector('[data-manage-formset]')) {
        import('./manageFormset.js').then(m => m.initManageFormsets());
    }
}

onLoad();
