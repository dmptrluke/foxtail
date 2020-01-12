from django.views.generic import ListView

from braces.views import SelectRelatedMixin

from apps.directory.mixins import SortableDirectoryMixin
from apps.directory.models import Profile


class ProfileListView(SelectRelatedMixin, SortableDirectoryMixin, ListView):
    model = Profile
    select_related = ['user']
    orderable_columns = ('user__username', 'region~country')
    orderable_columns_default = 'region~country'
    ordering_default = 'asc'


__all__ = ["ProfileListView"]
