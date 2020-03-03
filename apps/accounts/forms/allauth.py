from django.conf import settings

from allauth.account import forms as auth_forms
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Field, Layout, Row, Submit
from csp_helpers.mixins import CSPFormMixin


class SignupForm(CSPFormMixin, auth_forms.SignupForm):
    if settings.RECAPTCHA_ENABLED:
        if settings.RECAPTCHA_INVISIBLE:
            captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)
        else:
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
                Column(Field('username', autocomplete='username', placeholder='')),
                Column(Field('email', autocomplete='email', placeholder=''))
            ),
            Row(
                Column(Field('password1', autocomplete='new-password', placeholder='')),
                Column(Field('password2', autocomplete='new-password', placeholder=''))
            ),
            'captcha' if settings.RECAPTCHA_ENABLED else HTML('<!-- security! -->')

        )


class LoginForm(auth_forms.LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.error_text_inline = False
        self.helper.help_text_inline = False
        self.helper.use_custom_control = True

        self.helper.layout = Layout(
            Field('login', autocomplete='username'),
            Field('password', autocomplete='current-password'),
            'remember'
        )


class ResetPasswordForm(CSPFormMixin, auth_forms.ResetPasswordForm):
    if settings.RECAPTCHA_ENABLED:
        if settings.RECAPTCHA_INVISIBLE:
            captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)
        else:
            captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['captcha'].label = False

        self.helper.layout = Layout(
            'email',
            'captcha' if settings.RECAPTCHA_ENABLED else HTML('<!-- security! -->'),
            Submit('reset', 'Reset Password'),
        )


class ChangePasswordForm(auth_forms.ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.error_text_inline = False
        self.helper.help_text_inline = False

        self.helper.layout = Layout(
            Field('oldpassword', autocomplete='current-password', placeholder=''),
            Field('password1', autocomplete='new-password', placeholder=''),
            Field('password2', autocomplete='new-password', placeholder=''),
            Submit('change', 'Change Password'),
        )


class SetPasswordForm(auth_forms.ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.error_text_inline = False
        self.helper.help_text_inline = False

        self.helper.layout = Layout(
            Field('password1', autocomplete='new-password', placeholder=''),
            Field('password2', autocomplete='new-password', placeholder=''),
            Submit('set', 'Set Password'),
        )


__all__ = ['ChangePasswordForm', 'ResetPasswordForm', 'LoginForm', 'SignupForm']
