import { afterEach, describe, expect, it, vi } from 'vitest';

import { initManageFormset } from './manageFormset.js';

const sortableCreate = vi.hoisted(() => vi.fn());

vi.mock('sortablejs', () => ({
    default: {
        create: sortableCreate,
    },
}));

function render(html) {
    document.body.innerHTML = html;
    return document.querySelector('[data-manage-formset]');
}

function row(id) {
    return document.querySelector(`[data-row-id="${id}"]`);
}

function orderFor(id) {
    return row(id).querySelector('[data-manage-formset-order]').value;
}

afterEach(() => {
    document.body.innerHTML = '';
    sortableCreate.mockClear();
});

describe('initManageFormset', () => {
    it('adds rows from the empty form template and increments total forms', () => {
        const formset = render(`
            <form>
                <section data-manage-formset>
                    <input name="items-TOTAL_FORMS" value="1">
                    <div data-manage-formset-list>
                        <div data-manage-formset-row data-row-id="0">
                            <button type="button" data-manage-formset-remove>Remove</button>
                        </div>
                    </div>
                    <template data-manage-formset-empty-form>
                        <div data-manage-formset-row data-row-id="__prefix__">
                            <input name="items-__prefix__-name" value="">
                        </div>
                    </template>
                    <button data-manage-formset-add>Add</button>
                </section>
            </form>
        `);

        initManageFormset(formset);
        formset.querySelector('[data-manage-formset-add]').click();

        expect(formset.querySelector('input[name="items-TOTAL_FORMS"]').value).toBe('2');
        expect(formset.querySelector('[data-row-id="1"] input').name).toBe('items-1-name');
    });

    it('removes unsaved rows and marks persisted rows for deletion', () => {
        const formset = render(`
            <form>
                <section data-manage-formset data-manage-formset-orderable>
                    <input name="items-TOTAL_FORMS" value="2">
                    <div data-manage-formset-list>
                        <div data-manage-formset-row data-row-id="persisted">
                            <input name="items-0-order" value="0" data-manage-formset-order>
                            <input name="items-0-DELETE" type="checkbox">
                            <button type="button" data-manage-formset-remove>Remove</button>
                        </div>
                        <div data-manage-formset-row data-row-id="new">
                            <input name="items-1-order" value="1" data-manage-formset-order>
                            <button type="button" data-manage-formset-remove>Remove</button>
                        </div>
                    </div>
                </section>
            </form>
        `);

        initManageFormset(formset);
        row('persisted').querySelector('[data-manage-formset-remove]').click();
        row('new').querySelector('[data-manage-formset-remove]').click();

        expect(row('persisted').hidden).toBe(true);
        expect(row('persisted').querySelector('input[name="items-0-DELETE"]').checked).toBe(true);
        expect(row('new')).toBeNull();
    });

    it('moves visible rows and rewrites contiguous order values', () => {
        const formset = render(`
            <form>
                <section data-manage-formset data-manage-formset-orderable>
                    <input name="items-TOTAL_FORMS" value="3">
                    <div data-manage-formset-list>
                        <div data-manage-formset-row data-row-id="standard">
                            <input name="items-0-order" value="0" data-manage-formset-order>
                            <button type="button" data-manage-formset-move-up>Up</button>
                            <button type="button" data-manage-formset-move-down>Down</button>
                        </div>
                        <div data-manage-formset-row data-row-id="sponsor">
                            <input name="items-1-order" value="1" data-manage-formset-order>
                            <button type="button" data-manage-formset-move-up>Up</button>
                            <button type="button" data-manage-formset-move-down>Down</button>
                        </div>
                        <div data-manage-formset-row data-row-id="vip">
                            <input name="items-2-order" value="2" data-manage-formset-order>
                            <button type="button" data-manage-formset-move-up>Up</button>
                            <button type="button" data-manage-formset-move-down>Down</button>
                        </div>
                    </div>
                </section>
            </form>
        `);

        initManageFormset(formset);
        row('standard').querySelector('[data-manage-formset-move-down]').click();

        const visibleRows = [...formset.querySelectorAll('[data-manage-formset-row]')].map(row => row.dataset.rowId);
        expect(visibleRows).toEqual(['sponsor', 'standard', 'vip']);
        expect(orderFor('sponsor')).toBe('0');
        expect(orderFor('standard')).toBe('1');
        expect(orderFor('vip')).toBe('2');
        expect(row('sponsor').querySelector('[data-manage-formset-move-up]').disabled).toBe(true);
        expect(row('vip').querySelector('[data-manage-formset-move-down]').disabled).toBe(true);
    });

    it('initializes drag sorting with a handle and refreshes order after drag', () => {
        const formset = render(`
            <form>
                <section data-manage-formset data-manage-formset-orderable>
                    <input name="items-TOTAL_FORMS" value="2">
                    <div data-manage-formset-list>
                        <div data-manage-formset-row data-row-id="standard">
                            <button type="button" data-manage-formset-drag-handle>Drag</button>
                            <input name="items-0-order" value="99" data-manage-formset-order>
                        </div>
                        <div data-manage-formset-row data-row-id="sponsor">
                            <button type="button" data-manage-formset-drag-handle>Drag</button>
                            <input name="items-1-order" value="99" data-manage-formset-order>
                        </div>
                    </div>
                </section>
            </form>
        `);

        initManageFormset(formset);
        const [list, options] = sortableCreate.mock.calls[0];
        row('sponsor').after(row('standard'));
        options.onEnd();

        expect(list).toBe(formset.querySelector('[data-manage-formset-list]'));
        expect(options.handle).toBe('[data-manage-formset-drag-handle]');
        expect(options.draggable).toBe('[data-manage-formset-row]');
        expect(options.filter(new Event('pointerdown'), row('sponsor'))).toBe(false);
        expect(orderFor('sponsor')).toBe('0');
        expect(orderFor('standard')).toBe('1');
    });

    it('refreshes order before form submit', () => {
        const formset = render(`
            <form>
                <section data-manage-formset data-manage-formset-orderable>
                    <input name="items-TOTAL_FORMS" value="2">
                    <div data-manage-formset-list>
                        <div data-manage-formset-row data-row-id="standard">
                            <input name="items-0-order" value="99" data-manage-formset-order>
                        </div>
                        <div data-manage-formset-row data-row-id="sponsor">
                            <input name="items-1-order" value="99" data-manage-formset-order>
                        </div>
                    </div>
                </section>
            </form>
        `);

        initManageFormset(formset);
        formset.closest('form').dispatchEvent(new Event('submit'));

        expect(orderFor('standard')).toBe('0');
        expect(orderFor('sponsor')).toBe('1');
    });
});
