from django.contrib.admin import AdminSite
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache


class CustomAdminSite(AdminSite):
    site_header = 'Foxtail Admin'
    site_title = 'Foxtail Admin'

    @never_cache
    @login_required
    def login(self, request, extra_context=None):
        return super().login(self, request, extra_context=None)
