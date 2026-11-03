import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { initFooter } from './footer.js';

const root = document.documentElement;
const prepaint = readFileSync('src/templates/base.html', 'utf8').match(/<script nonce=".*?">([\s\S]*?)<\/script>/)[1];
let media;
let windowListeners;
let documentListeners;

beforeEach(() => {
    localStorage.clear();
    root.className = 'no-js theme-plum';
    root.dataset.defaultScheme = 'plum';
    delete root.dataset.pageScheme;
    delete root.dataset.bsTheme;
    media = Object.assign(new EventTarget(), { matches: false });
    vi.stubGlobal('matchMedia', vi.fn(() => media));
    windowListeners = vi.spyOn(window, 'addEventListener');
    documentListeners = vi.spyOn(document, 'addEventListener');
    document.body.innerHTML = `
        <div class="popup-wrapper">
            <a class="footer-popup-toggle" href="#">Theme</a>
            <div class="popup-theme" hidden>
                <button class="popup-theme-option" data-scheme="plum">Plum</button>
                <button class="popup-theme-option" data-scheme="coffee"><span>Coffee</span></button>
                <button class="popup-theme-option" data-style="default">Rounded</button>
                <button class="popup-theme-option" data-style="retro">Retro</button>
                <button class="popup-theme-option" data-mode="auto">Auto</button>
                <button class="popup-theme-option" data-mode="light">Light</button>
                <button class="popup-theme-option" data-mode="dark">Dark</button>
            </div>
        </div>
        <div class="popup-wrapper">
            <a class="footer-popup-toggle" data-debug-toggle href="#">Debug</a>
            <div class="popup-debug" hidden><span data-debug="theme"></span></div>
        </div>
    `;
});

afterEach(() => {
    for (const [target, spy] of [[window, windowListeners], [document, documentListeners]]) {
        for (const args of spy.mock.calls) target.removeEventListener(...args);
    }
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
});

function click(selector) {
    document.querySelector(selector).click();
}

function activeOptions() {
    return [...document.querySelectorAll('.popup-theme-option.active')].map(button => button.textContent);
}

describe('theme preferences', () => {
    // first paint and initialization agree on event, visitor, and site palette precedence
    it.each([
        ['', '', 'plum', 'auto', true],
        ['', 'coffee', 'coffee', 'dark', false],
        ['ocean', 'coffee', 'ocean', 'light', true],
    ])('resolves page "%s" and saved "%s" to %s in %s mode', (page, saved, expected, mode, systemDark) => {
        root.dataset.pageScheme = page;
        root.className = `no-js theme-${page || 'plum'}`;
        if (saved) localStorage.setItem('color-scheme', saved);
        localStorage.setItem('style-theme', 'retro');
        localStorage.setItem('dark-mode', mode);
        media.matches = systemDark;

        for (const initialize of [() => runInNewContext(prepaint, { document, localStorage, matchMedia }), initFooter]) {
            initialize();
            expect([...root.classList].sort()).toEqual(['js', `theme-${expected}`, 'theme-retro'].sort());
            expect(root.dataset.bsTheme).toBe(mode === 'light' ? undefined : 'dark');
            expect(localStorage.getItem('color-scheme')).toBe(saved || null);
        }
    });

    // auto follows system changes in both directions while explicit modes remain fixed
    it.each(['auto', 'light', 'dark'])('respects %s mode when the system preference changes', mode => {
        localStorage.setItem('dark-mode', mode);
        initFooter();
        expect(root.dataset.bsTheme).toBe(mode === 'dark' ? 'dark' : undefined);

        for (const matches of [true, false]) {
            media.matches = matches;
            media.dispatchEvent(new Event('change'));
            expect(root.dataset.bsTheme).toBe(mode === 'dark' || (mode === 'auto' && matches) ? 'dark' : undefined);
        }
    });

    // picker choices persist and switching back removes stale classes and active selections
    it('round trips color, style, and mode through the picker', () => {
        initFooter();
        click('.footer-popup-toggle');
        expect(activeOptions()).toEqual(['Plum', 'Rounded', 'Auto']);

        click('[data-scheme="coffee"] span');
        click('[data-style="retro"]');
        click('[data-mode="dark"]');
        expect(root.classList.contains('theme-coffee')).toBe(true);
        expect(root.classList.contains('theme-plum')).toBe(false);
        expect(root.classList.contains('theme-retro')).toBe(true);
        expect(root.dataset.bsTheme).toBe('dark');
        expect(activeOptions()).toEqual(['Coffee', 'Retro', 'Dark']);
        expect({ ...localStorage }).toEqual({ 'color-scheme': 'coffee', 'style-theme': 'retro', 'dark-mode': 'dark' });

        click('[data-style="default"]');
        click('[data-mode="light"]');
        expect(root.classList.contains('theme-retro')).toBe(false);
        expect(root.dataset.bsTheme).toBeUndefined();
        expect(activeOptions()).toEqual(['Coffee', 'Rounded', 'Light']);
        expect(localStorage.getItem('style-theme')).toBe('default');
        expect(localStorage.getItem('dark-mode')).toBe('light');
    });

    // changes from another tab update the theme and clearing storage restores all defaults
    it('applies storage changes and falls back when preferences are cleared', () => {
        initFooter();
        localStorage.setItem('color-scheme', 'coffee');
        localStorage.setItem('style-theme', 'retro');
        localStorage.setItem('dark-mode', 'dark');
        window.dispatchEvent(new StorageEvent('storage'));
        click('.footer-popup-toggle');
        expect(root.classList.contains('theme-coffee')).toBe(true);
        expect(root.classList.contains('theme-retro')).toBe(true);
        expect(root.dataset.bsTheme).toBe('dark');
        expect(activeOptions()).toEqual(['Coffee', 'Retro', 'Dark']);

        localStorage.clear();
        window.dispatchEvent(new StorageEvent('storage'));
        expect(root.classList.contains('theme-plum')).toBe(true);
        expect(root.classList.contains('theme-coffee')).toBe(false);
        expect(root.classList.contains('theme-retro')).toBe(false);
        expect(root.dataset.bsTheme).toBeUndefined();
    });

    // event branding survives preference changes and debug reports the palette actually displayed
    it('keeps the event palette until leaving the event page', () => {
        root.dataset.pageScheme = 'forest';
        localStorage.setItem('color-scheme', 'plum');
        initFooter();
        click('.footer-popup-toggle');
        click('[data-style="retro"]');
        click('[data-mode="dark"]');
        click('[data-scheme="coffee"]');
        expect(localStorage.getItem('color-scheme')).toBe('plum');

        localStorage.setItem('color-scheme', 'coffee');
        window.dispatchEvent(new StorageEvent('storage'));
        expect(root.classList.contains('theme-forest')).toBe(true);
        expect(root.classList.contains('theme-coffee')).toBe(false);
        expect(root.classList.contains('theme-retro')).toBe(true);
        expect(root.dataset.bsTheme).toBe('dark');
        expect(activeOptions()).toEqual(['Retro', 'Dark']);

        click('[data-debug-toggle]');
        expect(document.querySelector('[data-debug="theme"]').textContent).toBe('forest / retro / dark');
        expect(document.querySelector('.popup-theme').hidden).toBe(true);
        expect(document.querySelector('.popup-debug').hidden).toBe(false);
        document.body.click();
        expect(document.querySelector('.popup-debug').hidden).toBe(true);

        delete root.dataset.pageScheme;
        window.dispatchEvent(new StorageEvent('storage'));
        expect(root.classList.contains('theme-forest')).toBe(false);
        expect(root.classList.contains('theme-coffee')).toBe(true);
    });
});
