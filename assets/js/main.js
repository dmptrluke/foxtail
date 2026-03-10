import '@fontsource-variable/roboto';
import '@fontsource-variable/plus-jakarta-sans';
import '@fontsource-variable/plus-jakarta-sans/wght-italic.css';
import '../scss/index.scss';

import 'bootstrap/js/dist/dropdown';
import 'bootstrap/js/dist/collapse';
import 'bootstrap/js/dist/alert';
import Popover from 'bootstrap/js/dist/popover';
import Tooltip from 'bootstrap/js/dist/tooltip';

import 'colcade';

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

// --- Theme toggle ---

function initThemeToggle() {
    if (localStorage.getItem('theme') === 'sharp') {
        document.documentElement.classList.add('theme-sharp');
    }
    const btn = document.querySelector('.footer-theme-toggle');
    if (btn) {
        btn.addEventListener('click', () => {
            const isSharp = document.documentElement.classList.toggle('theme-sharp');
            localStorage.setItem('theme', isSharp ? 'sharp' : 'default');
        });
    }
}

// --- Init ---

function onLoad() {
    initThemeToggle();
    initBootstrap();
    initCharCounter();
    initProfileEdit();

    if (document.querySelector('[data-image-widget]')) {
        import('./imageWidget.js').then(m => m.initImageWidgets());
    }

    if (document.querySelector('[data-crop-widget]')) {
        import('./cropWidget.js').then(m => m.initCropWidgets());
    }

    if (document.querySelector('[data-map]')) {
        import('./map.js').then(m => m.initMaps());
    }
}

onLoad();
