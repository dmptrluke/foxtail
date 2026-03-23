from django.forms import Form

from csp_helpers.mixins import CSPFormMixin
from formguard.forms import GuardedFormMixin


class SocialLinkRedirectForm(GuardedFormMixin, CSPFormMixin, Form):
    guard_check_options = {
        'formguard.contrib.turnstile.TurnstileCheck': {
            'APPEARANCE': 'interaction-only',
            'CALLBACK': 'onTurnstileSuccess',
        },
    }
