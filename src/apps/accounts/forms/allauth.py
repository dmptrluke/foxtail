from django.conf import settings

from allauth.account import forms as auth_forms
from csp_helpers.mixins import CSPFormMixin
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible


class SignupForm(CSPFormMixin, auth_forms.SignupForm):
    if settings.RECAPTCHA_ENABLED:
        if settings.RECAPTCHA_INVISIBLE:
            captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)
        else:
            captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Required. 150 characters or fewer.'
        self.fields['email'].help_text = 'Required. This must be a valid email address for account activation.'
        if settings.RECAPTCHA_ENABLED:
            self.fields['captcha'].label = False


class ResetPasswordForm(CSPFormMixin, auth_forms.ResetPasswordForm):
    if settings.RECAPTCHA_ENABLED:
        if settings.RECAPTCHA_INVISIBLE:
            captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)
        else:
            captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if settings.RECAPTCHA_ENABLED:
            self.fields['captcha'].label = False


__all__ = ['ResetPasswordForm', 'SignupForm']
