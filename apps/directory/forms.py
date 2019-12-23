from django.forms import ModelForm

from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout, Submit

from .models import Profile


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('profile_URL', 'region')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.error_text_inline = False
        self.helper.help_text_inline = False

        self.helper.layout = Layout(
            Fieldset(
                'Basic Details',
                PrependedText('profile_URL', 'furry.nz/directory/'),
                Field('region', data_choices="true"),
            ),

            Submit('submit', 'Save Changes'),
        )
