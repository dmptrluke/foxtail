const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

function initPpoi(container, ppoiInput) {
    const preview = container.querySelector('.image-preview');
    if (!preview) return;

    preview.setAttribute('data-ppoi', '');

    let dot = preview.querySelector('.image-ppoi-dot');
    if (!dot) {
        dot = document.createElement('div');
        dot.className = 'image-ppoi-dot';
        preview.appendChild(dot);
    }

    const moveDot = (x, y) => {
        dot.style.left = `${x * 100}%`;
        dot.style.top = `${y * 100}%`;
    };

    const parts = (ppoiInput.value || '0.5x0.5').split('x');
    const px = parseFloat(parts[0]);
    const py = parseFloat(parts[1]);
    moveDot(isNaN(px) ? 0.5 : px, isNaN(py) ? 0.5 : py);

    preview.querySelector('img').addEventListener('click', e => {
        const rect = e.currentTarget.getBoundingClientRect();
        const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        const y = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));
        ppoiInput.value = `${x.toFixed(4)}x${y.toFixed(4)}`;
        moveDot(x, y);
    });
}

function showPreview(container, dataUrl) {
    let preview = container.querySelector('.image-preview');
    if (!preview) {
        preview = document.createElement('div');
        preview.className = 'image-preview mb-2';
        container.prepend(preview);
    }
    preview.innerHTML = `<img src="${dataUrl}" alt="" class="rounded">`;
    return preview;
}

export function initImageWidgets() {
    document.querySelectorAll('[data-image-widget]').forEach(container => {
        const fileInput = container.querySelector('input[type="file"]');
        if (!fileInput) return;

        const maxSize = parseInt(container.dataset.maxFileSize, 10) || 5 * 1024 * 1024;
        const ppoiFieldName = container.dataset.ppoiField || null;

        const ppoiInput = ppoiFieldName
            ? container.closest('form').querySelector(`[name="${ppoiFieldName}"]`)
            : null;

        if (ppoiInput) {
            initPpoi(container, ppoiInput);
        }

        fileInput.addEventListener('change', () => {
            const file = fileInput.files[0];
            if (!file) return;

            if (!ACCEPTED_TYPES.includes(file.type)) {
                alert('Please select a JPEG, PNG, or WebP image.');
                fileInput.value = '';
                return;
            }

            if (file.size > maxSize) {
                const sizeMB = (maxSize / (1024 * 1024)).toFixed(0);
                alert(`File is too large. Maximum size is ${sizeMB} MB.`);
                fileInput.value = '';
                return;
            }

            const reader = new FileReader();
            reader.onload = e => {
                showPreview(container, e.target.result);
                if (ppoiInput) {
                    ppoiInput.value = '0.5x0.5';
                    initPpoi(container, ppoiInput);
                }
            };
            reader.onerror = () => alert('Could not read the selected file.');
            reader.readAsDataURL(file);
        });
    });
}

export { ACCEPTED_TYPES, initPpoi, showPreview };
