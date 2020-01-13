from django.forms import ModelForm

from cjswidget.widgets import CJSWidget
from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit
from csp_helpers.mixins import CSPFormMixin

from .models import Profile


class ProfileForm(CSPFormMixin, ModelForm):
    class Meta:
        model = Profile
        fields = ('profile_URL', 'description', 'show_name', 'show_age', 'show_birthday', 'country', 'region')
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
                'show_name',
                'show_age',
                'show_birthday',
            ),
            Fieldset(
                'About',
                'description',
            ),
            Fieldset(
                'Location',
                'country',
                'region',
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
