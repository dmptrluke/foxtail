from django.views.generic import ListView

from braces.views import SelectRelatedMixin

from apps.directory.mixins import MultipleOrderableListMixin
from apps.directory.models import Profile


class ProfileListView(SelectRelatedMixin, MultipleOrderableListMixin, ListView):
    model = Profile
    select_related = ['user']
    orderable_columns = ('user__username', 'country~region')
    orderable_columns_default = 'user__username'


__all__ = ["ProfileListView"]
