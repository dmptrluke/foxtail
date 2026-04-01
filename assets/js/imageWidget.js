import { createDialog } from './dialog.js';

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const CROP_MAX_DIMENSION = 4096;
const QUALITY = 0.92;

class ImageUploadWidget {
    constructor(container) {
        this.container = container;
        this.fileInput = container.querySelector('input[type="file"]');
        this.maxSize = parseInt(container.dataset.maxFileSize, 10) || 20 * 1024 * 1024;

        // Feature detection from data attributes
        this.cropEnabled = container.hasAttribute('data-crop')
            || container.hasAttribute('data-crop-aspect-ratio');
        this.cropAspectRatio = parseFloat(container.dataset.cropAspectRatio) || NaN;

        const ppoiFieldName = container.dataset.ppoiField || null;
        this.ppoiInput = ppoiFieldName
            ? container.closest('form')?.querySelector(`[name="${ppoiFieldName}"]`)
            : null;

        // Crop state
        this.Cropper = null;
        this.dialog = null;
        this.dialogTitle = null;
        this.cropper = null;
        this.pendingFile = null;
        this.settingFiles = false;
        this.croppedCanvas = null;
        this.croppedMimeType = null;

        this.wireControls();
        this.fileInput.addEventListener('change', () => this.onFileChange());
    }

    // --- Controls ---

    wireControls() {
        const editBtn = this.container.querySelector('.image-edit-btn');
        if (editBtn) editBtn.addEventListener('click', () => this.openPpoiDialog());

        const removeBtn = this.container.querySelector('.image-remove-btn');
        if (removeBtn) {
            removeBtn.addEventListener('click', () => this.toggleRemove());
        }
    }

    toggleRemove() {
        const removeBtn = this.container.querySelector('.image-remove-btn');
        const checkbox = document.getElementById(removeBtn.dataset.checkboxId);
        if (!checkbox) return;
        const preview = this.container.querySelector('.image-preview');
        checkbox.checked = !checkbox.checked;
        if (preview) preview.classList.toggle('opacity-50', checkbox.checked);
        removeBtn.textContent = checkbox.checked ? 'Undo' : 'Remove';
        removeBtn.classList.toggle('btn-outline-danger', !checkbox.checked);
        removeBtn.classList.toggle('btn-outline-warning', checkbox.checked);
    }

    showEditButton() {
        const editBtn = this.container.querySelector('.image-edit-btn');
        if (editBtn) editBtn.classList.remove('d-none');
    }

    // --- Validation ---

    validateFile(file) {
        if (!ACCEPTED_TYPES.includes(file.type)) {
            alert('Please select a JPEG, PNG, or WebP image.');
            this.fileInput.value = '';
            return false;
        }
        if (file.size > this.maxSize) {
            const sizeMB = (this.maxSize / (1024 * 1024)).toFixed(0);
            alert(`File is too large. Maximum size is ${sizeMB} MB.`);
            this.fileInput.value = '';
            return false;
        }
        return true;
    }

    // --- PPOI ---

    ppoiCoordsFromClick(e, img) {
        const rect = img.getBoundingClientRect();
        return {
            x: Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width)),
            y: Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height)),
        };
    }

    // --- Preview ---

    showPreview(dataUrl) {
        let preview = this.container.querySelector('.image-preview');
        if (!preview) {
            preview = document.createElement('div');
            preview.className = 'image-preview';
            this.container.prepend(preview);
        }
        const roundClass = this.container.hasAttribute('data-preview-round') ? ' image-preview-round' : '';
        preview.className = `image-preview${roundClass}`;
        preview.innerHTML = `<img src="${dataUrl}" alt="" class="rounded">`;
        return preview;
    }

    // --- File change handler ---

    onFileChange() {
        if (this.settingFiles) return;
        const file = this.fileInput.files[0];
        if (!file) return;
        if (!this.validateFile(file)) return;

        const reader = new FileReader();
        reader.onerror = () => alert('Could not read the selected file.');
        reader.onload = (e) => {
            const dataUrl = e.target.result;
            if (this.cropEnabled) {
                this.pendingFile = file;
                this.openCropDialog(dataUrl);
            } else {
                this.showPreview(dataUrl);
                if (this.ppoiInput) {
                    this.showEditButton();
                    this.ppoiInput.value = '0.5x0.5';
                    this.openPpoiDialog();
                }
            }
        };
        reader.readAsDataURL(file);
    }

    // --- Dialog ---

    buildDialog() {
        const hasPpoi = !!this.ppoiInput;
        const { dialog, title, body, footer } = createDialog('Crop image');

        this.dialog = dialog;
        this.dialogTitle = title;

        body.innerHTML = `
            <div class="crop-step">
                <div class="image-crop-container">
                    <img class="crop-source" style="display: block;">
                </div>
            </div>
            <div class="ppoi-step d-none">
                <p class="text-body-secondary mb-2">Click to set the focal point for automatic crops.</p>
                <div class="image-ppoi-preview">
                    <img alt="">
                    <div class="image-ppoi-dot"></div>
                </div>
            </div>`;

        footer.innerHTML = `
            <button type="button" class="btn btn-secondary cancel-btn">Cancel</button>
            <button type="button" class="btn btn-secondary ppoi-back-btn d-none">Back</button>
            <button type="button" class="btn btn-primary crop-confirm-btn">${hasPpoi ? 'Next' : 'Crop'}</button>
            <button type="button" class="btn btn-primary ppoi-done-btn d-none">Done</button>`;

        dialog.addEventListener('close', () => this.onDialogClose());

        footer.querySelector('.cancel-btn').addEventListener('click', () => dialog.close());
        footer.querySelector('.crop-confirm-btn').addEventListener('click', () => this.onCropConfirm());

        if (hasPpoi) {
            footer.querySelector('.ppoi-back-btn').addEventListener('click', () => this.onPpoiBack());
            footer.querySelector('.ppoi-done-btn').addEventListener('click', () => this.onPpoiDone());

            const ppoiPreview = body.querySelector('.image-ppoi-preview');
            const ppoiImg = ppoiPreview.querySelector('img');
            ppoiImg.draggable = false;

            const updatePpoi = (e) => {
                const { x, y } = this.ppoiCoordsFromClick(e, ppoiImg);
                this.ppoiInput.value = `${x.toFixed(4)}x${y.toFixed(4)}`;
                const dot = ppoiPreview.querySelector('.image-ppoi-dot');
                dot.style.left = `${x * 100}%`;
                dot.style.top = `${y * 100}%`;
            };

            ppoiPreview.addEventListener('pointerdown', (e) => {
                if (e.target !== ppoiImg) return;
                ppoiPreview.setPointerCapture(e.pointerId);
                updatePpoi(e);
            });
            ppoiPreview.addEventListener('pointermove', (e) => {
                if (!ppoiPreview.hasPointerCapture(e.pointerId)) return;
                updatePpoi(e);
            });
        }
    }

    // --- Step management ---

    showStep(step, { showBack = false } = {}) {
        const d = this.dialog;
        const isCrop = step === 'crop';
        const isPpoi = step === 'ppoi';

        d.querySelector('.crop-step').classList.toggle('d-none', !isCrop);
        d.querySelector('.ppoi-step').classList.toggle('d-none', !isPpoi);
        this.dialogTitle.textContent = isCrop ? 'Crop image' : 'Set focal point';

        d.querySelector('.crop-confirm-btn').classList.toggle('d-none', !isCrop);
        d.querySelector('.cancel-btn').classList.toggle('d-none', isPpoi && showBack);

        const backBtn = d.querySelector('.ppoi-back-btn');
        if (backBtn) backBtn.classList.toggle('d-none', !showBack);

        const doneBtn = d.querySelector('.ppoi-done-btn');
        if (doneBtn) doneBtn.classList.toggle('d-none', !isPpoi);

        d.querySelectorAll('button').forEach(b => { b.disabled = false; });
    }

    setPpoiDot(x, y) {
        const dot = this.dialog.querySelector('.ppoi-step .image-ppoi-dot');
        dot.style.left = `${x * 100}%`;
        dot.style.top = `${y * 100}%`;
    }

    // --- Open flows ---

    openCropDialog(dataUrl) {
        if (!this.dialog) this.buildDialog();
        this.destroyCropper();
        this.showStep('crop');

        const img = this.dialog.querySelector('.crop-source');
        img.onload = () => this.initCropper();
        img.src = dataUrl;
        this.dialog.showModal();
    }

    openPpoiDialog() {
        if (!this.dialog) this.buildDialog();

        const previewImg = this.container.querySelector('.image-preview img');
        if (!previewImg) return;

        this.showStep('ppoi');

        const ppoiImg = this.dialog.querySelector('.ppoi-step img');
        ppoiImg.src = previewImg.src;

        const parts = (this.ppoiInput.value || '0.5x0.5').split('x');
        const px = parseFloat(parts[0]);
        const py = parseFloat(parts[1]);
        this.setPpoiDot(Number.isNaN(px) ? 0.5 : px, Number.isNaN(py) ? 0.5 : py);

        this.pendingFile = null;
        this.dialog.showModal();
    }

    onDialogClose() {
        this.destroyCropper();
        this.showStep('crop');

        if (this.pendingFile) {
            this.fileInput.value = '';
            this.pendingFile = null;
        }

        this.croppedCanvas = null;
        this.croppedMimeType = null;
    }

    // --- Cropper (lazy import) ---

    async initCropper() {
        if (!this.Cropper) {
            const [{ default: Cropper }] = await Promise.all([
                import('cropperjs'),
                import('cropperjs/dist/cropper.css'),
            ]);
            this.Cropper = Cropper;
        }
        this.destroyCropper();
        const img = this.dialog.querySelector('.crop-source');
        this.cropper = new this.Cropper(img, {
            aspectRatio: this.cropAspectRatio,
            viewMode: 1,
            autoCropArea: 1,
            responsive: true,
        });
    }

    destroyCropper() {
        if (this.cropper) {
            this.cropper.destroy();
            this.cropper = null;
        }
    }

    getCroppedOutput() {
        return this.cropper.getCroppedCanvas({
            maxWidth: CROP_MAX_DIMENSION,
            maxHeight: CROP_MAX_DIMENSION,
        });
    }

    // --- Crop confirm / PPOI step ---

    onCropConfirm() {
        if (!this.cropper || !this.pendingFile) return;
        this.dialog.querySelector('.crop-confirm-btn').disabled = true;

        const canvas = this.getCroppedOutput();
        const mimeType = this.pendingFile.type === 'image/png' ? 'image/png'
            : this.pendingFile.type === 'image/webp' ? 'image/webp'
            : 'image/jpeg';

        if (this.ppoiInput) {
            this.croppedCanvas = canvas;
            this.croppedMimeType = mimeType;
            this.destroyCropper();

            this.showStep('ppoi', { showBack: true });
            this.dialog.querySelector('.ppoi-step img').src = canvas.toDataURL(mimeType);
            this.ppoiInput.value = '0.5x0.5';
            this.setPpoiDot(0.5, 0.5);
        } else {
            this.finalize(canvas, mimeType);
        }
    }

    onPpoiBack() {
        this.showStep('crop');
        this.initCropper();
        this.croppedCanvas = null;
        this.croppedMimeType = null;
    }

    onPpoiDone() {
        if (!this.croppedCanvas) {
            this.dialog.close();
            return;
        }
        this.dialog.querySelector('.ppoi-done-btn').disabled = true;
        this.finalize(this.croppedCanvas, this.croppedMimeType);
    }

    // --- Finalize ---

    finalize(canvas, mimeType) {
        canvas.toBlob((blob) => {
            if (!blob || !this.dialog.open) {
                // biome-ignore lint/suspicious/noConsole: intentional user-facing diagnostic
                if (!blob) console.warn('Image crop failed: could not generate blob');
                return;
            }

            const extMap = { 'image/png': '.png', 'image/webp': '.webp', 'image/jpeg': '.jpg' };
            const ext = extMap[blob.type] || '.jpg';
            const name = (this.pendingFile.name.replace(/\.[^.]+$/, '') || 'image') + ext;
            const dt = new DataTransfer();
            dt.items.add(new File([blob], name, { type: blob.type }));
            this.settingFiles = true;
            this.fileInput.files = dt.files;
            this.settingFiles = false;

            this.showPreview(canvas.toDataURL(mimeType));
            this.showEditButton();

            this.pendingFile = null;
            this.dialog.close();
        }, mimeType, QUALITY);
    }
}

export function initImageWidgets() {
    document.querySelectorAll('[data-image-widget]').forEach(container => {
        if (container.dataset.imageWidgetInit) return;
        container.dataset.imageWidgetInit = '1';
        new ImageUploadWidget(container);
    });
}
