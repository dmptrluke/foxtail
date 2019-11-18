from django.contrib.admin import AdminSite
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.cache import never_cache


class CustomAdminSite(AdminSite):
    site_header = 'Foxtail Admin'
    site_title = 'Foxtail Admin'

    @never_cache
    def login(self, request, extra_context=None):
        if request.method == 'GET' and self.has_permission(request):
            # Already logged-in, redirect to admin index
            index_path = reverse('admin:index', current_app=self.name)
            return HttpResponseRedirect(index_path)
        else:
            login_path = reverse('account_login')
            return HttpResponseRedirect(login_path)
