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
        fields = ('profile_URL', 'region')
        widgets = {
            'region': CJSWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.error_text_inline = False
        self.helper.help_text_inline = False
        self.helper.include_media = False

        self.helper.layout = Layout(
            Fieldset(
                'Basic Details',
                PrependedText('profile_URL', 'furry.nz/directory/'),
                'region',
            ),
            Submit('submit', 'Save Changes'),
        )
