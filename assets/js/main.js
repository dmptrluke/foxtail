import '../scss/index.scss';

import 'bootstrap/js/dist/dropdown';
import 'bootstrap/js/dist/collapse';
import 'bootstrap/js/dist/alert';
import Popover from 'bootstrap/js/dist/popover';
import Tooltip from 'bootstrap/js/dist/tooltip';

import 'colcade';
import { UAParser } from 'ua-parser-js';

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
const STYLE_THEMES = ['default', 'sharp', 'retro', 'glass'];

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

    const picker = document.querySelector('.popup-theme');
    const debugPopup = document.querySelector('.popup-debug');
    const popups = [picker, debugPopup].filter(Boolean);

    // Populate client-side debug fields
    function updateDebugInfo() {
        if (!debugPopup) return;
        const set = (key, val) => {
            const el = debugPopup.querySelector(`[data-debug="${key}"]`);
            if (el) el.textContent = val;
        };
        const { browser, os, device } = UAParser(navigator.userAgent);
        set('screen', `${window.innerWidth}x${window.innerHeight}`);
        const browserPart = [browser.name, browser.version].filter(Boolean).join(' ');
        const osPart = [os.name, os.version].filter(Boolean).join(' ');
        set('browser', [browserPart, osPart].filter(Boolean).join(' / '));
        set('device', device.vendor ? [device.vendor, device.model].filter(Boolean).join(' ') : 'Desktop');
        const ls = (key, fallback) => localStorage.getItem(key) || fallback;
        set('theme', `${ls('color-scheme', 'plum')} / ${ls('style-theme', 'default')} / ${ls('dark-mode', 'auto')}`);
    }

    // Toggle buttons: each .footer-popup-toggle opens its sibling popup
    document.querySelectorAll('.footer-popup-toggle').forEach(toggle => {
        const popup = toggle.parentElement.querySelector('.popup-theme, .popup-debug');
        if (!popup) return;

        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            popups.forEach(p => { if (p !== popup) p.hidden = true; });
            popup.hidden = !popup.hidden;
            if (!popup.hidden && popup === picker) updatePickerState(picker);
            if (!popup.hidden && popup === debugPopup) updateDebugInfo();
        });
    });

    // Theme picker option clicks
    if (picker) {
        picker.addEventListener('click', (e) => {
            const btn = e.target.closest('.popup-theme-option');
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
    }

    // Close popups on outside click
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.popup-wrapper')) {
            popups.forEach(p => { p.hidden = true; });
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
