from django.forms import ModelForm

from cjswidget.widgets import CJSWidget
from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Fieldset, Layout, Submit
from csp_helpers.mixins import CSPFormMixin

from .models import Profile


class ProfileForm(CSPFormMixin, ModelForm):
    class Meta:
        model = Profile
        fields = ('profile_URL', 'description', 'description_privacy',
                  'country', 'region', 'location_privacy', 'age_privacy', 'birthday_privacy')

        widgets = {
            'country': CJSWidget(options={'shouldSort': False}),
            'region': CJSWidget(options={'shouldSort': False}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.error_text_inline = False
        self.helper.help_text_inline = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = Layout(
            Fieldset(
                'Basic Details',
                PrependedText('profile_URL', 'furry.nz/directory/'),
            ),
            Fieldset(
                'About',
                'description',
                'description_privacy'
            ),
            Fieldset(
                'Age and Birthday',
                'age_privacy',
                'birthday_privacy',
                HTML("""<div class="form-group row d-none" id="dob_warning"><div class="offset-lg-2 col-lg-8">
        <div class="alert alert-warning" role="alert">
            Sharing both your age and birthday will allow others to determine your full date of birth.
        </div></div></div>
        """)
            ),
            Fieldset(
                'Location',
                'country',
                'region',
                'location_privacy'
            ),
            Submit('submit', 'Save Changes'),
        )


class ProfileCreateForm(CSPFormMixin, ModelForm):
    class Meta:
        model = Profile
        fields = ('profile_URL',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.error_text_inline = False
        self.helper.help_text_inline = False

        self.helper.layout = Layout(
            PrependedText('profile_URL', 'furry.nz/directory/'),
            Submit('create', 'Create Profile'),
        )
