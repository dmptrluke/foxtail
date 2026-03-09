// --- Image crop widget ---
//
// Flow: file selected → validate → open Bootstrap modal with Cropper.js →
// user confirms → crop to blob → replace file input → show inline preview.
//
// If ppoi_field is set, also shows a draggable focus-point dot on the preview
// that writes "x y" coordinates to a hidden image_ppoi form field.

import Cropper from 'cropperjs';
import 'cropperjs/dist/cropper.css';
import Modal from 'bootstrap/js/dist/modal';

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

// Creates and appends a crop modal to the document body.
// Created lazily on first file selection and reused for subsequent crops within the same widget.
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

// Attaches a clickable PPOI dot to an existing preview image.
// Reads the current PPOI from ppoiInput (two floats separated by "x", e.g. "0.3x0.7")
// and positions the dot accordingly. Clicking the preview updates both the dot
// and the hidden input. Called on page load (existing image) and after each crop.
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

        // Modal state is shared across file selections for this widget instance
        let modalEl = null;
        let bsModal = null;
        let confirmBtn = null;
        let cropper = null;

        // Resolve the hidden PPOI input upfront (even if there's no preview yet,
        // so it's available after a fresh crop on a new image)
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

            if (!modalEl) {
                modalEl = createCropModal();
                bsModal = new Modal(modalEl);
                confirmBtn = modalEl.querySelector('.crop-confirm');
            }

            // Read file as data URL to set as Cropper source.
            // Blob URLs are avoided here as they require blob: in img-src CSP.
            const reader = new FileReader();
            reader.onload = e => {
                const img = modalEl.querySelector('.crop-source');
                img.src = e.target.result;

                // Cropper must be initialised after the modal is visible so it
                // can measure the image dimensions correctly
                modalEl.addEventListener('shown.bs.modal', () => {
                    if (cropper) cropper.destroy();
                    cropper = new Cropper(img, {
                        aspectRatio,
                        viewMode: 1,       // crop box stays within the canvas
                        autoCropArea: 1,   // crop box fills the canvas initially
                        responsive: true,
                    });
                }, { once: true });

                bsModal.show();
            };
            reader.readAsDataURL(file);

            const onCrop = () => {
                const canvas = cropper.getCroppedCanvas({ maxWidth: 1024, maxHeight: 1024 });

                // toBlob is async; encoding format matches the source file type.
                // If the browser doesn't support WebP canvas export it falls back to PNG.
                const mimeType = file.type === 'image/png' ? 'image/png'
                    : file.type === 'image/webp' ? 'image/webp'
                    : 'image/jpeg';
                canvas.toBlob(blob => {
                    if (!blob) return;

                    // Replace the file input's value with the cropped blob so the
                    // form submits the cropped image rather than the original
                    const extMap = { 'image/png': '.png', 'image/webp': '.webp', 'image/jpeg': '.jpg' };
                    const ext = extMap[blob.type] || '.jpg';
                    const name = (file.name.replace(/\.[^.]+$/, '') || 'image') + ext;
                    const dt = new DataTransfer();
                    dt.items.add(new File([blob], name, { type: blob.type }));
                    fileInput.files = dt.files;

                    // Show inline preview; create the wrapper if this is a fresh upload
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

                    cropper.destroy();
                    cropper = null;
                    bsModal.hide();
                }, mimeType, 0.9);
            };
            // { once: true } prevents double-crop if the user re-selects a file
            // while the modal is open
            confirmBtn.addEventListener('click', onCrop, { once: true });

            // Clean up if the modal is dismissed without confirming
            modalEl.addEventListener('hidden.bs.modal', () => {
                confirmBtn.removeEventListener('click', onCrop);
                if (cropper) {
                    cropper.destroy();
                    cropper = null;
                }
            }, { once: true });
        });
    });
}
