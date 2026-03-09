import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/400-italic.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
import '../scss/index.scss';

import 'bootstrap/js/dist/dropdown';
import 'bootstrap/js/dist/collapse';
import 'bootstrap/js/dist/alert';
import Popover from 'bootstrap/js/dist/popover';
import Tooltip from 'bootstrap/js/dist/tooltip';

import 'colcade';

import { initCropWidgets } from './cropWidget.js';
import { initProfileEdit } from './profileEdit.js';

// --- Bootstrap component initialization ---

function initBootstrap() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => new Tooltip(el));
    document.querySelectorAll('[data-bs-toggle="popover"]').forEach(el => new Popover(el));
}

// --- Comment character counter ---

function initCharCounter() {
    const textInput = document.getElementById('id_text');
    if (textInput) {
        textInput.addEventListener('keyup', () => {
            const hint = document.getElementById('hint_id_text');
            if (!hint) return;
            const remaining = textInput.maxLength - textInput.value.length;
            const plural = remaining === 1 ? '' : 's';
            hint.textContent = `${remaining} character${plural} remaining.`;
        });
    }
}

// --- Init ---

function onLoad() {
    initBootstrap();
    initCharCounter();
    initProfileEdit();
    initCropWidgets();
}

// ES module scripts are deferred — DOM is always ready by the time this runs
onLoad();
