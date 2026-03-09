from django.contrib.auth.mixins import LoginRequiredMixin

from rules.contrib.views import PermissionRequiredMixin


class PermissionMixin(PermissionRequiredMixin, LoginRequiredMixin):
    raise_exception = True
