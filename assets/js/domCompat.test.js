import { describe, expect, it, vi } from 'vitest';

import { closestElement, onMediaQueryChange } from './domCompat.js';

describe('closestElement', () => {
    it('returns closest match when target is an element', () => {
        document.body.innerHTML = `
            <div class="popup-wrapper">
                <button id="btn"><span id="child">Theme</span></button>
            </div>
        `;

        const child = document.getElementById('child');
        const wrapper = closestElement(child, '.popup-wrapper');

        expect(wrapper).toBe(document.querySelector('.popup-wrapper'));
    });

    it('returns closest match when target is a text node', () => {
        document.body.innerHTML = `
            <div class="popup-wrapper">
                <button id="btn"><span id="child">Theme</span></button>
            </div>
        `;

        const textNode = document.getElementById('child').firstChild;
        const wrapper = closestElement(textNode, '.popup-wrapper');

        expect(wrapper).toBe(document.querySelector('.popup-wrapper'));
    });
});

describe('onMediaQueryChange', () => {
    it('uses addEventListener when available', () => {
        const addEventListener = vi.fn();
        const addListener = vi.fn();
        const mediaQueryList = { addEventListener, addListener };
        const callback = vi.fn();

        onMediaQueryChange(mediaQueryList, callback);

        expect(addEventListener).toHaveBeenCalledWith('change', callback);
        expect(addListener).not.toHaveBeenCalled();
    });

    it('falls back to addListener when addEventListener is unavailable', () => {
        const addListener = vi.fn();
        const mediaQueryList = { addListener };
        const callback = vi.fn();

        onMediaQueryChange(mediaQueryList, callback);

        expect(addListener).toHaveBeenCalledWith(callback);
    });
});
