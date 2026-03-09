// --- Image crop widget ---
//
// Flow: file selected → validate → open Bootstrap modal with Cropper.js →
// user confirms → crop to blob → replace file input → show inline preview.
//
// If ppoi_field is set, also shows a clickable focus-point dot on the preview
// that writes "x y" coordinates to a hidden image_ppoi form field.

import Cropper from 'cropperjs';
import 'cropperjs/dist/cropper.css';
import Modal from 'bootstrap/js/dist/modal';

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

function createCropModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.tabIndex = -1;
    modal.innerHTML = `
        <div class="modal-dialog modal-lg modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Crop Image</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="image-crop-container">
                        <img class="crop-source" style="display: block;">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary crop-confirm">Crop</button>
                </div>
            </div>
        </div>`;
    document.body.appendChild(modal);
    return modal;
}

// Attaches a clickable PPOI dot to a preview image.
// PPOI format is two floats separated by "x", e.g. "0.3x0.7".
function initPpoi(container, ppoiInput) {
    const preview = container.querySelector('.image-crop-preview');
    if (!preview) return;

    // data-ppoi triggers the crosshair cursor via CSS
    preview.setAttribute('data-ppoi', '');

    const dot = document.createElement('div');
    dot.className = 'image-crop-ppoi-dot';
    preview.appendChild(dot);

    const moveDot = (x, y) => {
        dot.style.left = `${x * 100}%`;
        dot.style.top = `${y * 100}%`;
    };

    // Parse stored "0.5x0.5" value; fall back to centre if missing or malformed
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

export function initCropWidgets() {
    document.querySelectorAll('[data-crop-widget]').forEach(container => {
        const fileInput = container.querySelector('input[type="file"]');
        if (!fileInput) return;

        const aspectRatio = parseFloat(container.dataset.cropAspectRatio);
        const maxSize = parseInt(container.dataset.cropMaxSize, 10) || 5 * 1024 * 1024;
        const ppoiFieldName = container.dataset.ppoiField || null;

        // --- State ---
        let modalEl = null;
        let bsModal = null;
        let cropper = null;
        let pendingFile = null;

        // Resolved upfront so it's available after a fresh crop on a new image
        const ppoiInput = ppoiFieldName
            ? container.closest('form').querySelector(`[name="${ppoiFieldName}"]`)
            : null;

        if (ppoiInput) {
            initPpoi(container, ppoiInput);
        }

        // --- Cropper lifecycle ---
        function destroyCropper() {
            if (cropper) {
                cropper.destroy();
                cropper = null;
            }
        }

        function initCropper() {
            destroyCropper();
            const img = modalEl.querySelector('.crop-source');
            cropper = new Cropper(img, {
                aspectRatio,
                viewMode: 1,
                autoCropArea: 1,
                responsive: true,
            });
        }

        // --- Modal (created lazily, listeners registered once to avoid stacking) ---
        function initModal() {
            modalEl = createCropModal();
            bsModal = new Modal(modalEl);
            const confirmBtn = modalEl.querySelector('.crop-confirm');

            // Cropper must be initialised after the modal is visible so it
            // can measure the image dimensions correctly
            modalEl.addEventListener('shown.bs.modal', initCropper);
            modalEl.addEventListener('hidden.bs.modal', () => {
                destroyCropper();
                // If the user cancelled (no crop confirmed), clear the file input
                // so the form doesn't submit the uncropped original
                if (pendingFile) {
                    fileInput.value = '';
                    pendingFile = null;
                }
            });

            confirmBtn.addEventListener('click', () => {
                if (!cropper || !pendingFile) return;
                const canvas = cropper.getCroppedCanvas({ maxWidth: 1024, maxHeight: 1024 });

                const mimeType = pendingFile.type === 'image/png' ? 'image/png'
                    : pendingFile.type === 'image/webp' ? 'image/webp'
                    : 'image/jpeg';
                canvas.toBlob(blob => {
                    if (!blob) return;

                    // Swap the file input to the cropped blob via DataTransfer
                    const extMap = { 'image/png': '.png', 'image/webp': '.webp', 'image/jpeg': '.jpg' };
                    const ext = extMap[blob.type] || '.jpg';
                    const name = (pendingFile.name.replace(/\.[^.]+$/, '') || 'image') + ext;
                    const dt = new DataTransfer();
                    dt.items.add(new File([blob], name, { type: blob.type }));
                    fileInput.files = dt.files;

                    let preview = container.querySelector('.image-crop-preview');
                    if (!preview) {
                        preview = document.createElement('div');
                        preview.className = 'image-crop-preview mb-2';
                        container.prepend(preview);
                    }
                    preview.innerHTML = `<img src="${canvas.toDataURL(mimeType)}" alt="" class="rounded">`;

                    // After crop the focus point resets to centre; user can click to adjust
                    if (ppoiInput) {
                        ppoiInput.value = '0.5x0.5';
                        initPpoi(container, ppoiInput);
                    }

                    // Null pendingFile before hide so the hidden handler
                    // knows this was a confirmed crop, not a cancel
                    pendingFile = null;
                    bsModal.hide();
                }, mimeType, 0.9);
            });
        }

        // --- File selection handler ---
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

            if (!modalEl) initModal();

            pendingFile = file;

            // Destroy before re-read so re-selection while modal is open works
            destroyCropper();

            // Data URLs avoid needing blob: in img-src CSP
            const reader = new FileReader();
            reader.onload = e => {
                const img = modalEl.querySelector('.crop-source');
                img.src = e.target.result;

                // If the modal is already visible, re-init the cropper directly
                // since shown.bs.modal won't fire again.
                if (modalEl.classList.contains('show')) {
                    initCropper();
                } else {
                    bsModal.show();
                }
            };
            reader.readAsDataURL(file);
        });
    });
}
