from django.conf import settings
from django.forms import ModelForm, SelectDateWidget

from allauth.account import forms as auth_forms
from captcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Field, Fieldset, Layout, Row, Submit

from apps.accounts.models import User


class SignupForm(auth_forms.SignupForm):
    if settings.RECAPTCHA_ENABLED:
        captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.error_text_inline = False
        self.helper.help_text_inline = False

        self.fields['username'].help_text = "Required. 150 characters or fewer."
        self.fields['email'].help_text = "Required. This must be a valid email address for account activation."

        if settings.RECAPTCHA_ENABLED:
            self.fields['captcha'].label = False

        self.helper.layout = Layout(
            Row(
                Column(Field('username', autocomplete='username', placeholder=''), css_class='col-md-6'),
                Column(Field('email', autocomplete='email', placeholder=''), css_class='col-md-6')
            ),
            Row(
                Column(Field('password1', autocomplete='new-password', placeholder=''), css_class='col-md-6'),
                Column(Field('password2', autocomplete='new-password', placeholder=''), css_class='col-md-6')
            ),
            Row(
                Column('captcha', css_class='col-md-12'),
            ) if settings.RECAPTCHA_ENABLED else HTML('<!-- security! -->')

        )


class LoginForm(auth_forms.LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.error_text_inline = False
        self.helper.help_text_inline = False
        self.use_custom_control = True

        self.helper.layout = Layout(
            Field('login', autocomplete='username'),
            Field('password', autocomplete='current-password'),
            'remember'
        )


class ResetPasswordForm(auth_forms.ResetPasswordForm):
    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True

        self.fields['captcha'].label = False

        self.helper.layout = Layout(
            'email',
            'captcha'
        )


class UserForm(ModelForm):
    class Meta:
        model = User
        widgets = {
            'date_of_birth': SelectDateWidget(years=range(1920, 2011),
                                              empty_label=("Year", "Month", "Day")),
        }
        fields = ('username', 'date_of_birth', 'gender', 'full_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.error_text_inline = False
        self.helper.help_text_inline = False

        self.helper.layout = Layout(
            Fieldset(
                'Basic Details',
                Row(
                    Column('username', css_class='col-md-6'),
                )
            ),
            Fieldset(
                'Personal Information',
                HTML('<p class="small">This information is optional.</p>'),
                Row(
                    Column(Field('full_name', autocomplete='name'), css_class='col-md-6'),
                    Column(Field('gender', autocomplete='sex'), css_class='col-md-6'),
                ),
                Row(
                    Column('date_of_birth', css_class='col-md-6'),
                )
            ),
            Submit('submit', 'Save Changes'),
        )
