// --- Profile edit (directory) ---

const Privacy = Object.freeze({ PUBLIC: '0', SIGNED_IN: '5', NOBODY: '10' });

export function initProfileEdit() {
    if (typeof country_choices === 'undefined') return;

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
        const checkPrivacy = () => {
            const bothPublic = agePrivacy.value !== Privacy.NOBODY && birthdayPrivacy.value !== Privacy.NOBODY;
            dobWarning.classList.toggle('d-none', !bothPublic);
        };
        agePrivacy.addEventListener('change', checkPrivacy);
        birthdayPrivacy.addEventListener('change', checkPrivacy);
        checkPrivacy();
    }
}
