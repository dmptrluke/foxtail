import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/400-italic.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
import '../scss/index.scss';

import Cropper from 'cropperjs';
import 'cropperjs/dist/cropper.css';

import Dropdown from 'bootstrap/js/dist/dropdown';
import Collapse from 'bootstrap/js/dist/collapse';
import Alert from 'bootstrap/js/dist/alert';
import Modal from 'bootstrap/js/dist/modal';
import Popover from 'bootstrap/js/dist/popover';
import Tooltip from 'bootstrap/js/dist/tooltip';

import 'colcade';

// --- Bootstrap component initialization ---

function initBootstrap() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
        new Tooltip(el);
    });

    document.querySelectorAll('[data-bs-toggle="popover"]').forEach(function (el) {
        new Popover(el);
    });
}

// --- Comment character counter ---

function initCharCounter() {
    var textInput = document.getElementById('id_text');
    if (textInput) {
        textInput.addEventListener('keyup', function () {
            var remaining = this.maxLength - this.value.length;
            var plural = remaining === 1 ? '' : 's';
            document.getElementById('hint_id_text').textContent =
                remaining + ' character' + plural + ' remaining.';
        });
    }
}

// --- Profile edit (directory) ---

function initProfileEdit() {
    if (typeof country_choices === 'undefined') return;

    if (country_choices.getValue(true) === 'NZ') {
        region_choices.enable();
    } else {
        region_choices.disable();
    }
    country_choices.passedElement.element.addEventListener('change', function (e) {
        if (e.detail.value === 'NZ') {
            region_choices.enable();
        } else {
            region_choices.disable();
            region_choices.setChoiceByValue('');
        }
    });

    var dob_warning = document.getElementById('dob_warning');
    var age_privacy = document.getElementById('id_age_privacy');
    var birthday_privacy = document.getElementById('id_birthday_privacy');

    if (dob_warning && age_privacy && birthday_privacy) {
        function checkPrivacy() {
            if (age_privacy.value !== '10' && birthday_privacy.value !== '10') {
                dob_warning.classList.remove('d-none');
            } else {
                dob_warning.classList.add('d-none');
            }
        }
        age_privacy.addEventListener('change', checkPrivacy);
        birthday_privacy.addEventListener('change', checkPrivacy);
        checkPrivacy();
    }
}

// --- Image crop widget ---

var ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

function createCropModal() {
    var modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.tabIndex = -1;
    modal.innerHTML =
        '<div class="modal-dialog modal-lg modal-dialog-centered">' +
            '<div class="modal-content">' +
                '<div class="modal-header">' +
                    '<h5 class="modal-title">Crop Image</h5>' +
                    '<button type="button" class="btn-close" data-bs-dismiss="modal"></button>' +
                '</div>' +
                '<div class="modal-body">' +
                    '<div class="image-crop-container">' +
                        '<img class="crop-source" style="max-width: 100%; display: block;">' +
                    '</div>' +
                '</div>' +
                '<div class="modal-footer">' +
                    '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>' +
                    '<button type="button" class="btn btn-primary crop-confirm">Crop</button>' +
                '</div>' +
            '</div>' +
        '</div>';
    document.body.appendChild(modal);
    return modal;
}

function initCropWidgets() {
    document.querySelectorAll('[data-crop-widget]').forEach(function (container) {
        var fileInput = container.querySelector('input[type="file"]');
        if (!fileInput) return;

        var aspectRatio = parseFloat(container.dataset.cropAspectRatio) || NaN;
        var maxSize = parseInt(container.dataset.cropMaxSize, 10) || 5 * 1024 * 1024;

        var modalEl = null;
        var bsModal = null;
        var cropper = null;

        fileInput.addEventListener('change', function () {
            var file = this.files[0];
            if (!file) return;

            if (!ACCEPTED_TYPES.includes(file.type)) {
                alert('Please select a JPEG, PNG, or WebP image.');
                this.value = '';
                return;
            }

            if (file.size > maxSize) {
                var sizeMB = (maxSize / (1024 * 1024)).toFixed(0);
                alert('File is too large. Maximum size is ' + sizeMB + ' MB.');
                this.value = '';
                return;
            }

            if (!modalEl) {
                modalEl = createCropModal();
                bsModal = new Modal(modalEl);
            }

            var reader = new FileReader();
            reader.onload = function (e) {
                var img = modalEl.querySelector('.crop-source');
                img.src = e.target.result;

                modalEl.addEventListener('shown.bs.modal', function () {
                    if (cropper) {
                        cropper.destroy();
                    }
                    cropper = new Cropper(img, {
                        aspectRatio: isNaN(aspectRatio) ? NaN : aspectRatio,
                        viewMode: 1,
                        autoCropArea: 1,
                        responsive: true,
                    });
                }, { once: true });

                bsModal.show();
            };
            reader.readAsDataURL(file);

            var confirmBtn = modalEl.querySelector('.crop-confirm');
            function onCrop() {
                confirmBtn.removeEventListener('click', onCrop);

                var canvas = cropper.getCroppedCanvas({
                    maxWidth: 1024,
                    maxHeight: 1024,
                });

                canvas.toBlob(function (blob) {
                    if (!blob) return;

                    var ext = blob.type === 'image/png' ? '.png' : '.jpg';
                    var name = (file.name.replace(/\.[^.]+$/, '') || 'avatar') + ext;
                    var croppedFile = new File([blob], name, { type: blob.type });

                    var dt = new DataTransfer();
                    dt.items.add(croppedFile);
                    fileInput.files = dt.files;

                    var preview = container.querySelector('.image-crop-preview');
                    if (!preview) {
                        preview = document.createElement('div');
                        preview.className = 'image-crop-preview mb-2';
                        container.insertBefore(preview, container.firstChild);
                    }
                    preview.innerHTML = '<img src="' + canvas.toDataURL() + '" alt="" class="rounded">';

                    cropper.destroy();
                    cropper = null;
                    bsModal.hide();
                }, file.type === 'image/png' ? 'image/png' : 'image/jpeg', 0.9);
            }
            confirmBtn.addEventListener('click', onCrop);

            modalEl.addEventListener('hidden.bs.modal', function () {
                confirmBtn.removeEventListener('click', onCrop);
                if (cropper) {
                    cropper.destroy();
                    cropper = null;
                }
            }, { once: true });
        });
    });
}

// --- Init ---

function on_load() {
    initBootstrap();
    initCharCounter();
    initProfileEdit();
    initCropWidgets();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', on_load);
} else {
    on_load();
}
