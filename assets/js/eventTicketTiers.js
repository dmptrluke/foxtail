function rowHasTicketData(row) {
    const fieldNames = ['name', 'price', 'available_from', 'available_until'];
    const hasTextValue = fieldNames.some((name) => {
        const input = row.querySelector(`[name$="-${name}"]`);
        return input && input.value.trim() !== '';
    });
    const soldOut = row.querySelector('input[name$="-is_sold_out"]');
    return hasTextValue || Boolean(soldOut?.checked);
}

function rowIsPersisted(row) {
    const idInput = row.querySelector('input[name$="-id"]');
    return idInput && idInput.value !== '';
}

function refreshOrders(container) {
    let order = 0;
    container.querySelectorAll('[data-ticket-form]').forEach((row) => {
        const orderInput = row.querySelector('input[name$="-order"]');
        if (!orderInput) return;
        if (!rowIsPersisted(row) && !rowHasTicketData(row)) {
            orderInput.value = '';
            return;
        }
        orderInput.value = order;
        order += 1;
    });
}

function initTicketFormset(formset) {
    const list = formset.querySelector('[data-ticket-list]');
    const template = formset.querySelector('[data-ticket-empty-form]');
    const addButton = formset.querySelector('[data-ticket-add]');
    const totalForms = formset.querySelector('input[name$="-TOTAL_FORMS"]');
    if (!list || !template || !addButton || !totalForms) return;

    addButton.addEventListener('click', () => {
        const index = Number.parseInt(totalForms.value, 10);
        const html = template.innerHTML.replaceAll('__prefix__', index);
        list.insertAdjacentHTML('beforeend', html);
        totalForms.value = index + 1;
        refreshOrders(list);
    });

    list.addEventListener('click', (event) => {
        const button = event.target.closest('[data-ticket-remove]');
        if (!button) return;

        const row = button.closest('[data-ticket-form]');
        const deleteInput = row.querySelector('input[name$="-DELETE"]');
        if (deleteInput) deleteInput.checked = true;
        row.hidden = true;
        refreshOrders(list);
    });

    refreshOrders(list);
}

export function initEventTicketTiers() {
    document.querySelectorAll('[data-ticket-formset]').forEach(initTicketFormset);
}
