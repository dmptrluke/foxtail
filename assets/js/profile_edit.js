let age_privacy;
let birthday_privacy;

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
    age_privacy = document.getElementById('id_age_privacy');
    birthday_privacy = document.getElementById('id_birthday_privacy');

    age_privacy.addEventListener('change', checkboxes);
    birthday_privacy.addEventListener('change', checkboxes);
    checkboxes()
}

function checkboxes() {
    if (age_privacy.value !== "10"  && birthday_privacy.value !== "10")  {
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
