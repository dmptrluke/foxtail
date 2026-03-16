import { getCsrfToken } from './csrf.js';

function updateButtons(group, status) {
    group.querySelectorAll('[data-interest-btn]').forEach(btn => {
        const isActive = btn.dataset.interestBtn === status;
        btn.classList.toggle('active', isActive);
    });
}

function updateCounts(group, data) {
    const interested = group.querySelector('[data-interest-count="interested"]');
    const going = group.querySelector('[data-interest-count="going"]');
    if (interested) interested.textContent = data.interested_count || '';
    if (going) going.textContent = data.going_count || '';
}

export function initEventInterest() {
    document.querySelectorAll('[data-interest-url]').forEach(group => {
        const url = group.dataset.interestUrl;
        const buttons = group.querySelectorAll('[data-interest-btn]');

        updateButtons(group, group.dataset.status);

        buttons.forEach(btn => {
            btn.addEventListener('click', async () => {
                const btnStatus = btn.dataset.interestBtn;
                const currentStatus = group.dataset.status || '';
                const nextStatus = currentStatus === btnStatus ? '' : btnStatus;

                const prevStatus = currentStatus;
                group.dataset.status = nextStatus;
                updateButtons(group, nextStatus);

                try {
                    const res = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCsrfToken(),
                        },
                        body: JSON.stringify({ status: nextStatus || undefined }),
                    });
                    if (!res.ok) throw new Error();
                    const data = await res.json();
                    updateCounts(group, data);
                } catch {
                    group.dataset.status = prevStatus;
                    updateButtons(group, prevStatus);
                }
            });
        });
    });
}
