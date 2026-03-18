import logging
import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import signing
from django.forms import CharField, HiddenInput
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from rules.contrib.views import PermissionRequiredMixin

logger = logging.getLogger(__name__)


class PermissionMixin(PermissionRequiredMixin, LoginRequiredMixin):
    """Require login + object-level permission, return 403 on failure (not redirect)"""

    raise_exception = True


class HtmxMixin:
    """Return an HTMX partial instead of a redirect when HX-Request is present.

    Subclasses set htmx_template and call self.htmx_response(context).
    """

    htmx_template = None

    def is_htmx(self):
        return self.request.headers.get('HX-Request') == 'true'

    def htmx_response(self, context=None, template=None):
        ctx = context or {}
        ctx['is_partial'] = True
        return TemplateResponse(self.request, template or self.htmx_template, ctx)


class HoneypotFormMixin:
    """Add a hidden honeypot field and a signed timestamp to detect bots."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['website'] = CharField(required=False)
        self.fields['hp_loaded'] = CharField(
            widget=HiddenInput,
            initial=signing.dumps(time.time()),
            required=False,
        )


class HoneypotViewMixin:
    """Silently discard submissions that trip the honeypot or are submitted too fast."""

    honeypot_min_seconds = 3
    honeypot_success_message = 'Your message has been sent.'

    def is_honeypot(self, form):
        """Return True if the submission looks like a bot."""
        addr = self.request.META.get('REMOTE_ADDR', 'unknown')

        if form.cleaned_data.get('website'):
            logger.warning('Honeypot triggered from %s', addr)
            return True

        try:
            loaded = signing.loads(form.cleaned_data.get('hp_loaded', ''), max_age=3600)
            if time.time() - loaded < self.honeypot_min_seconds:
                logger.warning('Honeypot timer triggered from %s', addr)
                return True
        except (signing.BadSignature, TypeError):
            logger.warning('Honeypot bad signature from %s', addr)
            return True

        return False

    def honeypot_success(self):
        """Return a fake success response indistinguishable from a real one."""
        from django.contrib import messages

        messages.success(self.request, self.honeypot_success_message)
        return HttpResponseRedirect(self.get_success_url())
