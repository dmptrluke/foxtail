const Privacy = Object.freeze({ PUBLIC: '0', SIGNED_IN: '5', NOBODY: '10' });

export function initProfileEdit() {
    if (typeof country_choices === 'undefined' || typeof region_choices === 'undefined') return;

    if (country_choices.getValue(true) === 'NZ') {
        region_choices.enable();
    } else {
        region_choices.disable();
    }
    country_choices.passedElement.element.addEventListener('change', e => {
        if (e.detail.value === 'NZ') {
            region_choices.enable();
        } else {
            region_choices.disable();
            region_choices.setChoiceByValue('');
        }
    });

    const dobWarning = document.getElementById('dob_warning');
    const agePrivacy = document.getElementById('id_age_privacy');
    const birthdayPrivacy = document.getElementById('id_birthday_privacy');

    if (dobWarning && agePrivacy && birthdayPrivacy) {
        const updateDobWarning = () => {
            const bothExposed = agePrivacy.value !== Privacy.NOBODY
                && birthdayPrivacy.value !== Privacy.NOBODY;
            dobWarning.hidden = !bothExposed;
        };
        agePrivacy.addEventListener('change', updateDobWarning);
        birthdayPrivacy.addEventListener('change', updateDobWarning);
        updateDobWarning();
    }
}
