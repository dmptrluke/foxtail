from django.views.generic import ListView

from braces.views import OrderableListMixin

from apps.directory.models import Profile


class ProfileListView(OrderableListMixin, ListView):
    model = Profile
    orderable_columns = ('user__username', 'region')
    orderable_columns_default = 'user__username'


__all__ = ["ProfileListView"]
