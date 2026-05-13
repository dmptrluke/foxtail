const FORMSET_INITIALIZED = 'adminFormsetInitialized';

function getParts(formset) {
    return {
        list: formset.querySelector('[data-admin-formset-list]'),
        template: formset.querySelector('template[data-admin-formset-empty-form]'),
        addButton: formset.querySelector('[data-admin-formset-add]'),
        totalForms: formset.querySelector('input[name$="-TOTAL_FORMS"]'),
    };
}

function rows(list) {
    return [...list.querySelectorAll('[data-admin-formset-row]')];
}

function isDeleted(row) {
    return row.hidden || Boolean(row.querySelector('input[name$="-DELETE"]')?.checked);
}

function visibleRows(list) {
    return rows(list).filter(row => !isDeleted(row));
}

function orderInput(row) {
    return row.querySelector('[data-admin-formset-order], input[name$="-order"]');
}

function updateMoveButtonStates(formset) {
    const { list } = getParts(formset);
    if (!list) return;

    const orderedRows = visibleRows(list);
    orderedRows.forEach((row, index) => {
        const moveUp = row.querySelector('[data-admin-formset-move-up]');
        const moveDown = row.querySelector('[data-admin-formset-move-down]');
        if (moveUp) moveUp.disabled = index === 0;
        if (moveDown) moveDown.disabled = index === orderedRows.length - 1;
    });
}

function refreshOrder(formset) {
    if (!formset.hasAttribute('data-admin-formset-orderable')) return;

    const { list } = getParts(formset);
    if (!list) return;

    visibleRows(list).forEach((row, index) => {
        const input = orderInput(row);
        if (input) input.value = index;
    });
    updateMoveButtonStates(formset);
}

function addRow(formset) {
    const { list, template, totalForms } = getParts(formset);
    if (!list || !template || !totalForms) return;

    const index = Number.parseInt(totalForms.value, 10);
    if (Number.isNaN(index)) return;

    const html = template.innerHTML.replaceAll('__prefix__', index);
    list.insertAdjacentHTML('beforeend', html);
    totalForms.value = index + 1;
    refreshOrder(formset);
}

function removeRow(formset, row) {
    const deleteInput = row.querySelector('input[name$="-DELETE"]');
    if (deleteInput) {
        deleteInput.checked = true;
        row.hidden = true;
    } else {
        row.remove();
    }
    refreshOrder(formset);
}

function moveRow(formset, row, direction) {
    const { list } = getParts(formset);
    if (!list) return;

    const orderedRows = visibleRows(list);
    const currentIndex = orderedRows.indexOf(row);
    const targetIndex = currentIndex + direction;
    if (currentIndex === -1 || targetIndex < 0 || targetIndex >= orderedRows.length) return;

    const targetRow = orderedRows[targetIndex];
    if (direction < 0) {
        list.insertBefore(row, targetRow);
    } else {
        list.insertBefore(targetRow, row);
    }
    row.querySelector('[data-admin-formset-move-up], [data-admin-formset-move-down]')?.focus();
    refreshOrder(formset);
}

function handleListClick(formset, event) {
    const removeButton = event.target.closest('[data-admin-formset-remove]');
    const moveUpButton = event.target.closest('[data-admin-formset-move-up]');
    const moveDownButton = event.target.closest('[data-admin-formset-move-down]');
    const button = removeButton || moveUpButton || moveDownButton;
    if (!button) return;

    const row = button.closest('[data-admin-formset-row]');
    if (!row) return;

    if (removeButton) {
        removeRow(formset, row);
    } else if (moveUpButton) {
        moveRow(formset, row, -1);
    } else if (moveDownButton) {
        moveRow(formset, row, 1);
    }
}

export function initAdminFormset(formset) {
    if (formset.dataset[FORMSET_INITIALIZED] === 'true') return;

    const { list, addButton, totalForms } = getParts(formset);
    if (!list || !totalForms) return;

    addButton?.addEventListener('click', () => addRow(formset));
    list.addEventListener('click', event => handleListClick(formset, event));

    const ownerForm = formset.closest('form');
    ownerForm?.addEventListener('submit', () => refreshOrder(formset));

    refreshOrder(formset);
    formset.dataset[FORMSET_INITIALIZED] = 'true';
}

export function initAdminFormsets(root = document) {
    root.querySelectorAll('[data-admin-formset]').forEach(initAdminFormset);
}
