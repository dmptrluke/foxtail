import os
from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse

from unfold.sites import UnfoldAdminSite


class CustomAdminSite(UnfoldAdminSite):
    site_header = 'Foxtail'
    site_title = 'Foxtail'

    def login(self, request, extra_context=None):
        if request.method == 'GET' and self.has_permission(request):
            return HttpResponseRedirect(reverse('admin:index', current_app=self.name))
        url = reverse('account_login')
        params = urlencode({'next': reverse('admin:index', current_app=self.name)})
        return HttpResponseRedirect(f'{url}?{params}')


def environment_callback(request):
    """Return environment label for unfold's header badge."""
    env = os.environ.get('SENTRY_ENVIRONMENT', '')
    if env == 'staging':
        return ['Staging', 'warning']
    if env == 'production':
        return ['Production', 'info']
    if settings.DEBUG:
        return ['Development', 'warning']
    return None
