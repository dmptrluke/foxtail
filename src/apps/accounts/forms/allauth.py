from allauth.account import forms as auth_forms
from csp_helpers.mixins import CSPFormMixin
from formguard.forms import GuardedFormMixin


class SignupForm(GuardedFormMixin, CSPFormMixin, auth_forms.SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Required. 150 characters or fewer.'
        self.fields['email'].help_text = 'Required. This must be a valid email address for account activation.'
        self.fields['password1'].help_text = "At least 8 characters. Can't be all numbers or a common password."


class ResetPasswordForm(GuardedFormMixin, CSPFormMixin, auth_forms.ResetPasswordForm):
    pass


__all__ = ['ResetPasswordForm', 'SignupForm']
