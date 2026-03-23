from django.forms import Form

from csp_helpers.mixins import CSPFormMixin
from formguard.forms import GuardedFormMixin


class SocialLinkRedirectForm(GuardedFormMixin, CSPFormMixin, Form):
    pass
