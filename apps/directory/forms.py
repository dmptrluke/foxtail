from django.forms import ModelForm

from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Fieldset, Layout, Row, Submit

from .models import Profile


class ProfileForm(ModelForm):
    class Meta:
        model = Profile

        fields = ('profile_URL',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.error_text_inline = False
        self.helper.help_text_inline = False

        self.helper.layout = Layout(
            Fieldset(
                'Basic Details',
                Row(
                    Column(PrependedText('profile_URL', 'furry.nz/directory/'), css_class='col-md-6'),
                )
            ),

            Submit('submit', 'Save Changes'),
        )
