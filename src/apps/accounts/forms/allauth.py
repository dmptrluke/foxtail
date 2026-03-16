from django.conf import settings

from allauth.account import forms as auth_forms
from csp_helpers.mixins import CSPFormMixin
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible


class SignupForm(CSPFormMixin, auth_forms.SignupForm):
    if settings.RECAPTCHA_INVISIBLE:
        captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)
    else:
        captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Required. 150 characters or fewer.'
        self.fields['email'].help_text = 'Required. This must be a valid email address for account activation.'
        self.fields['password1'].help_text = "At least 8 characters. Can't be all numbers or a common password."
        self.fields['captcha'].label = False


class ResetPasswordForm(CSPFormMixin, auth_forms.ResetPasswordForm):
    if settings.RECAPTCHA_INVISIBLE:
        captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)
    else:
        captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['captcha'].label = False


__all__ = ['ResetPasswordForm', 'SignupForm']
