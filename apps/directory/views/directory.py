from django.views.generic import ListView

from braces.views import OrderableListMixin, SelectRelatedMixin

from apps.directory.models import Profile


class ProfileListView(SelectRelatedMixin, OrderableListMixin, ListView):
    model = Profile
    select_related = ['user']
    orderable_columns = ('user__username', 'region')
    orderable_columns_default = 'user__username'


__all__ = ["ProfileListView"]
