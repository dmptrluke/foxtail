import '../scss/index.scss';

import 'bootstrap/js/dist/dropdown';
import 'bootstrap/js/dist/collapse';
import 'bootstrap/js/dist/alert';

import 'colcade';
import htmx from 'htmx.org';
import { getCsrfToken } from './csrf.js';

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

// --- Theme switcher ---

const COLOR_SCHEMES = ['plum', 'coffee', 'autumn', 'forest', 'slate'];
const STYLE_THEMES = ['default', 'sharp', 'retro', 'glass'];
const DEFAULT_COLOR_SCHEME = document.documentElement.dataset.defaultScheme;

function applyTheme() {
    const root = document.documentElement;
    const scheme = localStorage.getItem('color-scheme') || DEFAULT_COLOR_SCHEME;
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
    const scheme = localStorage.getItem('color-scheme') || DEFAULT_COLOR_SCHEME;
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
    async function updateDebugInfo() {
        if (!debugPopup) return;
        const set = (key, val) => {
            const el = debugPopup.querySelector(`[data-debug="${key}"]`);
            if (el) el.textContent = val;
        };
        set('screen', `${window.innerWidth}x${window.innerHeight}`);
        const uad = navigator.userAgentData;
        if (uad) {
            const hints = await uad.getHighEntropyValues(['platform', 'platformVersion', 'model']);
            const brand = uad.brands?.find(b => !b.brand.includes('Not'))?.brand;
            set('browser', [brand, hints.platform, hints.platformVersion].filter(Boolean).join(' / '));
            set('device', hints.model || (uad.mobile ? 'Mobile' : 'Desktop'));
        } else {
            set('browser', navigator.userAgent);
            set('device', 'Unknown');
        }
        const ls = (key, fallback) => localStorage.getItem(key) || fallback;
        set('theme', `${ls('color-scheme', DEFAULT_COLOR_SCHEME)} / ${ls('style-theme', 'default')} / ${ls('dark-mode', 'auto')}`);
    }

    // Toggle buttons: each .footer-popup-toggle opens its sibling popup
    document.querySelectorAll('.footer-popup-toggle').forEach(toggle => {
        const popup = toggle.parentElement.querySelector('.popup-theme, .popup-debug');
        if (!popup) return;

        toggle.addEventListener('click', (e) => {
            e.preventDefault();
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

document.addEventListener('htmx:afterSwap', () => initCharCounter());

// --- Init ---

function onLoad() {
    initThemeToggle();
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
}

onLoad();
