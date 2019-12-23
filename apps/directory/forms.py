from django.forms import ModelForm

from crispy_forms.helper import FormHelper

from .models import Profile


class ProfileForm(ModelForm):
    class Meta:
        model = Profile

        fields = ('profile_URL', 'region')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.error_text_inline = False
        self.helper.help_text_inline = False
