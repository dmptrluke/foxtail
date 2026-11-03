const COLOR_SCHEMES = ['plum', 'slate', 'coffee', 'forest', 'autumn', 'berry', 'tui', 'twilight', 'dusk', 'ocean', 'contrast'];
const STYLE_THEMES = ['default', 'retro', 'glass', 'terminal'];

function getColorScheme() {
    const root = document.documentElement;
    return root.dataset.pageScheme || localStorage.getItem('color-scheme') || root.dataset.defaultScheme;
}

function applyTheme() {
    const root = document.documentElement;
    const scheme = getColorScheme();
    const style = localStorage.getItem('style-theme') || 'default';
    const mode = localStorage.getItem('dark-mode') || 'auto';

    COLOR_SCHEMES.forEach(s => root.classList.remove(`theme-${s}`));
    root.classList.add(`theme-${scheme}`);

    STYLE_THEMES.forEach(s => { if (s !== 'default') root.classList.remove(`theme-${s}`); });
    if (style !== 'default') root.classList.add(`theme-${style}`);

    const dark = mode === 'dark' || (mode === 'auto' && matchMedia('(prefers-color-scheme: dark)').matches);
    if (dark) {
        root.dataset.bsTheme = 'dark';
    } else {
        delete root.dataset.bsTheme;
    }
}

function updatePickerState(picker) {
    const scheme = getColorScheme();
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

export function initFooter() {
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
        set('theme', `${getColorScheme()} / ${ls('style-theme', 'default')} / ${ls('dark-mode', 'auto')}`);
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

            if (btn.dataset.scheme && !document.documentElement.dataset.pageScheme) {
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
