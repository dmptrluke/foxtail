from urllib.parse import urlencode

from django.contrib.admin import AdminSite
from django.http import HttpResponseRedirect
from django.urls import reverse


class CustomAdminSite(AdminSite):
    site_header = 'Foxtail Admin'
    site_title = 'Foxtail Admin'

    def login(self, request, extra_context=None):
        if request.method == 'GET' and self.has_permission(request):
            return HttpResponseRedirect(reverse('admin:index', current_app=self.name))
        url = reverse('account_login')
        params = urlencode({'next': reverse('admin:index', current_app=self.name)})
        return HttpResponseRedirect(f'{url}?{params}')
