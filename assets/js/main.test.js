import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('bootstrap/js/dist/dropdown', () => ({}));
vi.mock('bootstrap/js/dist/collapse', () => ({}));
vi.mock('bootstrap/js/dist/alert', () => ({}));
vi.mock('colcade', () => ({}));
vi.mock('htmx.org', () => ({
    default: {
        config: {},
    },
}));
vi.mock('./csrf.js', () => ({
    getCsrfToken: () => null,
}));

function render() {
    document.documentElement.dataset.defaultScheme = 'plum';
    document.body.innerHTML = `
        <div class="popup-wrapper">
            <a class="footer-popup-toggle" href="#" role="button">Theme</a>
            <div class="popup-theme" hidden></div>
        </div>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbar"></button>
        <div class="collapse navbar-collapse" id="navbar"></div>
    `;
}

describe('main.js theme initialization', () => {
    beforeEach(() => {
        vi.resetModules();
        localStorage.clear();
        render();
    });

    afterEach(() => {
        document.body.innerHTML = '';
        delete window.htmx;
    });

    it('supports matchMedia listeners on browsers with addListener only', async () => {
        const addListener = vi.fn();
        window.matchMedia = vi.fn(() => ({
            matches: false,
            addListener,
        }));

        await import('./main.js');
        document.querySelector('.footer-popup-toggle').click();

        expect(addListener).toHaveBeenCalledTimes(1);
        expect(document.querySelector('.popup-theme').hidden).toBe(false);
    });
});
