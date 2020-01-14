let age_checkbox;
let birthday_checkbox;

let dob_warning;

function on_load() {
    // Country Choices
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

    // DOB warning
    dob_warning = document.getElementById('dob_warning');
    age_checkbox = document.getElementById('id_show_age');
    birthday_checkbox = document.getElementById('id_show_birthday');

    age_checkbox.addEventListener('change', checkboxes);
    birthday_checkbox.addEventListener('change', checkboxes);
}

function checkboxes() {
    if (age_checkbox.checked && birthday_checkbox.checked)  {
        dob_warning.classList.remove('d-none');
    } else {
        dob_warning.classList.add('d-none');
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', on_load);
} else {
    on_load();
}
