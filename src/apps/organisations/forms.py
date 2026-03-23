from django.forms import Form

from csp_helpers.mixins import CSPFormMixin
from formguard.forms import GuardedFormMixin


class SocialLinkRedirectForm(GuardedFormMixin, CSPFormMixin, Form):
    # Only Turnstile verification; no timestamp/interaction checks (auto-submitted by callback)
    guard_checks = [
        'formguard.contrib.turnstile.TurnstileCheck',
    ]
    guard_check_options = {
        'formguard.contrib.turnstile.TurnstileCheck': {
            'APPEARANCE': 'interaction-only',
            'CALLBACK': 'onTurnstileSuccess',
        },
    }
