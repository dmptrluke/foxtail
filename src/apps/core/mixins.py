from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.response import TemplateResponse

from rules.contrib.views import PermissionRequiredMixin


class PermissionMixin(PermissionRequiredMixin, LoginRequiredMixin):
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
