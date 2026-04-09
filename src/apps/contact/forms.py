from django.forms import CharField, EmailField, Form, Textarea

from csp_helpers.mixins import CSPFormMixin
from formguard.forms import GuardedFormMixin


class ContactForm(GuardedFormMixin, CSPFormMixin, Form):
    name = CharField(required=True)
    email = EmailField(required=True)
    message = CharField(required=True, widget=Textarea)

    def __init__(self, *args, **kwargs):
        from formguard.contrib.turnstile.checks import TurnstileCheck

        super().__init__(*args, **kwargs)
        # skip Turnstile for authenticated users
        if self.request and self.request.user.is_authenticated:
            self._checks = [c for c in self._checks if not isinstance(c, TurnstileCheck)]
