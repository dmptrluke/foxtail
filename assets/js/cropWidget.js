import Cropper from 'cropperjs';
import 'cropperjs/dist/cropper.css';
import Modal from 'bootstrap/js/dist/modal';

import { ACCEPTED_TYPES, initPpoi, showPreview } from './imageWidget.js';

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

export function initCropWidgets() {
    document.querySelectorAll('[data-crop-widget]').forEach(container => {
        const fileInput = container.querySelector('input[type="file"]');
        if (!fileInput) return;

        const aspectRatio = parseFloat(container.dataset.cropAspectRatio);
        const maxSize = parseInt(container.dataset.maxFileSize, 10) || 5 * 1024 * 1024;
        const ppoiFieldName = container.dataset.ppoiField || null;

        let modalEl = null;
        let bsModal = null;
        let cropper = null;
        let pendingFile = null;

        const ppoiInput = ppoiFieldName
            ? container.closest('form').querySelector(`[name="${ppoiFieldName}"]`)
            : null;

        if (ppoiInput) {
            initPpoi(container, ppoiInput);
        }

        function destroyCropper() {
            if (cropper) {
                cropper.destroy();
                cropper = null;
            }
        }

        function startCropper() {
            destroyCropper();
            const img = modalEl.querySelector('.crop-source');
            cropper = new Cropper(img, {
                aspectRatio,
                viewMode: 1,
                autoCropArea: 1,
                responsive: true,
            });
        }

        function initModal() {
            modalEl = createCropModal();
            bsModal = new Modal(modalEl);
            const confirmBtn = modalEl.querySelector('.crop-confirm');

            modalEl.addEventListener('shown.bs.modal', startCropper);
            modalEl.addEventListener('hidden.bs.modal', () => {
                destroyCropper();
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
                    if (!blob || !pendingFile) return;

                    const extMap = { 'image/png': '.png', 'image/webp': '.webp', 'image/jpeg': '.jpg' };
                    const ext = extMap[blob.type] || '.jpg';
                    const name = (pendingFile.name.replace(/\.[^.]+$/, '') || 'image') + ext;
                    const dt = new DataTransfer();
                    dt.items.add(new File([blob], name, { type: blob.type }));
                    fileInput.files = dt.files;

                    showPreview(container, canvas.toDataURL(mimeType));

                    if (ppoiInput) {
                        ppoiInput.value = '0.5x0.5';
                        initPpoi(container, ppoiInput);
                    }

                    pendingFile = null;
                    bsModal.hide();
                }, mimeType, 0.9);
            });
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

            if (!modalEl) initModal();

            pendingFile = file;
            destroyCropper();

            const reader = new FileReader();
            reader.onload = e => {
                const img = modalEl.querySelector('.crop-source');
                img.src = e.target.result;

                if (modalEl.classList.contains('show')) {
                    startCropper();
                } else {
                    bsModal.show();
                }
            };
            reader.onerror = () => alert('Could not read the selected file.');
            reader.readAsDataURL(file);
        });
    });
}
