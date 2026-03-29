/**
 * Create a native <dialog> with standard header/body/footer chrome.
 * Returns { dialog, title, body, footer, close } for the caller to populate.
 */
export function createDialog(titleText, { className = '' } = {}) {
    const el = document.createElement('dialog');
    el.className = `app-dialog${className ? ` ${className}` : ''}`;
    el.innerHTML = `
        <div class="dialog-header">
            <h5 class="dialog-title">${titleText}</h5>
            <button type="button" class="btn-close" aria-label="Close"></button>
        </div>
        <div class="dialog-body"></div>
        <div class="dialog-footer"></div>`;
    document.body.appendChild(el);

    // Close on backdrop click
    el.addEventListener('click', (e) => {
        if (e.target === el) el.close();
    });

    // Close button
    el.querySelector('.btn-close').addEventListener('click', () => el.close());

    return {
        dialog: el,
        title: el.querySelector('.dialog-title'),
        body: el.querySelector('.dialog-body'),
        footer: el.querySelector('.dialog-footer'),
        close: () => el.close(),
    };
}
