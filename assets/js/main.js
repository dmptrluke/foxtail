import '../scss/index.scss';

import 'bootstrap/js/dist/dropdown';
import 'bootstrap/js/dist/collapse';
import 'bootstrap/js/dist/alert';
import Popover from 'bootstrap/js/dist/popover';
import Tooltip from 'bootstrap/js/dist/tooltip';

import 'colcade';

// --- Bootstrap component initialization ---

function initBootstrap() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => new Tooltip(el));
    document.querySelectorAll('[data-bs-toggle="popover"]').forEach(el => new Popover(el));
}

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

// --- Theme switcher ---

const COLOR_SCHEMES = ['plum', 'coffee', 'autumn', 'forest', 'slate'];
const STYLE_THEMES = ['default', 'sharp', 'retro'];

function applyTheme() {
    const root = document.documentElement;
    const scheme = localStorage.getItem('color-scheme') || 'plum';
    const style = localStorage.getItem('style-theme') || 'default';
    const mode = localStorage.getItem('dark-mode') || 'auto';

    COLOR_SCHEMES.forEach(s => root.classList.remove(`theme-${s}`));
    if (scheme !== 'plum') root.classList.add(`theme-${scheme}`);

    STYLE_THEMES.forEach(s => { if (s !== 'default') root.classList.remove(`theme-${s}`); });
    if (style !== 'default') root.classList.add(`theme-${style}`);

    const dark = mode === 'dark' || (mode === 'auto' && matchMedia('(prefers-color-scheme: dark)').matches);
    if (dark) {
        root.setAttribute('data-bs-theme', 'dark');
    } else {
        root.removeAttribute('data-bs-theme');
    }
}

function updatePickerState(picker) {
    const scheme = localStorage.getItem('color-scheme') || 'plum';
    const style = localStorage.getItem('style-theme') || 'default';
    const mode = localStorage.getItem('dark-mode') || 'auto';

    picker.querySelectorAll('[data-scheme]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.scheme === scheme);
    });
    picker.querySelectorAll('[data-style]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.style === style);
    });
    picker.querySelectorAll('[data-mode]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });
}

function initThemeToggle() {
    applyTheme();
    matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);
    window.addEventListener('storage', applyTheme);

    const toggle = document.querySelector('.footer-theme-toggle');
    const picker = document.querySelector('.theme-picker');
    if (!toggle || !picker) return;

    toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        const wasOpen = !picker.hidden;
        picker.hidden = wasOpen;
        if (!wasOpen) updatePickerState(picker);
    });

    picker.addEventListener('click', (e) => {
        const btn = e.target.closest('.theme-picker-option');
        if (!btn) return;

        if (btn.dataset.scheme) {
            localStorage.setItem('color-scheme', btn.dataset.scheme);
        } else if (btn.dataset.style) {
            localStorage.setItem('style-theme', btn.dataset.style);
        } else if (btn.dataset.mode) {
            localStorage.setItem('dark-mode', btn.dataset.mode);
        }
        applyTheme();
        updatePickerState(picker);
    });

    document.addEventListener('click', (e) => {
        if (!picker.hidden && !e.target.closest('.footer-theme-wrapper')) {
            picker.hidden = true;
        }
    });
}

// --- Init ---

function onLoad() {
    initThemeToggle();
    initBootstrap();
    initCharCounter();
    if (document.getElementById('id_age_privacy')) {
        import('./profileEdit.js').then(m => m.initProfileEdit());
    }

    if (document.querySelector('[data-image-widget]')) {
        import('./imageWidget.js').then(m => m.initImageWidgets());
    }

    if (document.querySelector('[data-crop-widget]')) {
        import('./cropWidget.js').then(m => m.initCropWidgets());
    }

    if (document.querySelector('[data-map]')) {
        import('./map.js').then(m => m.initMaps());
    }

    if (document.querySelector('[data-autocomplete-url]')) {
        import('./autocomplete.js').then(m => m.initAutocomplete());
    }
}

onLoad();
