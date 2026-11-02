import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { initAutocomplete } from './autocomplete.js';

function render(organisation = '', series = '') {
    document.body.innerHTML = `
        <form>
            <select id="id_organisation">
                <option value=""></option>
                <option value="1">First group</option>
                <option value="2">Second group</option>
            </select>
            <select id="id_series" data-autocomplete-url="/autocomplete/series/"
                    data-autocomplete-parent="id_organisation" data-autocomplete-parent-param="organisation">
                <option value=""></option>
                ${series ? `<option value="${series}" selected>Existing series</option>` : ''}
            </select>
        </form>
    `;
    const parent = document.getElementById('id_organisation');
    parent.value = organisation;
    initAutocomplete();
    return { parent, control: document.getElementById('id_series').tomselect };
}

function choose(parent, value) {
    parent.value = value;
    parent.dispatchEvent(new Event('change', { bubbles: true }));
}

beforeEach(() => {
    vi.useFakeTimers();
    vi.stubGlobal('fetch', vi.fn(url => Promise.resolve({
        json: () => Promise.resolve({ results: [{ id: `${url.searchParams.get('organisation')}0`, text: 'Series' }] }),
    })));
});

afterEach(() => {
    document.querySelectorAll('select').forEach(el => el.tomselect?.destroy());
    document.body.innerHTML = '';
    vi.unstubAllGlobals();
    vi.useRealTimers();
});

describe('dependent autocomplete', () => {
    // changing organisation clears the previous series and loads only the new organisation's choices
    it('requires an organisation and refreshes choices when it changes', async () => {
        const { parent, control } = render();
        expect(control.isDisabled).toBe(true);
        choose(parent, '1');
        await vi.advanceTimersByTimeAsync(350);
        expect(control.isDisabled).toBe(false);
        expect(control.options['10']).toBeDefined();
        control.addItem('10');

        choose(parent, '2');
        expect(control.getValue()).toBe('');
        await vi.advanceTimersByTimeAsync(350);
        expect(control.options['10']).toBeUndefined();
        expect(control.options['20']).toBeDefined();

        choose(parent, '');
        expect(control.isDisabled).toBe(true);
        expect(control.getValue()).toBe('');
    });

    // editing an event preserves its selected series while loading matching choices
    it('preserves the existing series on initialisation', async () => {
        const { control } = render('1', '10');
        await vi.advanceTimersByTimeAsync(350);
        expect(control.getValue()).toBe('10');
    });

    // a delayed response for an earlier organisation cannot restore its choices
    it('ignores responses for a previous organisation', async () => {
        let resolveFirst;
        fetch.mockImplementationOnce(() => new Promise(resolve => { resolveFirst = resolve; }));
        const { parent, control } = render();
        choose(parent, '1');
        await vi.advanceTimersByTimeAsync(350);
        choose(parent, '2');
        await vi.advanceTimersByTimeAsync(350);
        resolveFirst({ json: () => Promise.resolve({ results: [{ id: '10', text: 'Old series' }] }) });
        await vi.advanceTimersByTimeAsync(0);
        expect(control.options['10']).toBeUndefined();
        expect(control.options['20']).toBeDefined();
    });
});
