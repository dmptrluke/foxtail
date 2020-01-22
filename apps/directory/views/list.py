from django.db.models import Case, When
from django.views.generic import ListView

from apps.directory.models import Profile


class ProfileListView(ListView):
    model = Profile
    order_by = None
    ordering = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order_by"] = self.order_by
        context["ordering"] = self.ordering
        return context

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')

        self.ordering = self.request.GET.get("ordering", 'asc')

        if self.request.GET.get("order_by") in ('location', 'name'):
            self.order_by = self.request.GET.get("order_by")
        else:
            self.order_by = 'location'

        rules = []
        columns = []

        if self.order_by == 'name':
            columns = ['user__username']

        elif self.order_by == 'location':
            columns = ['region', 'country']
            if self.ordering == 'desc':
                rules.append(Case(
                    When(country='NZ', then=1),
                    When(country='', then=2),
                    default=0))
            else:
                rules.append(Case(
                    When(country='NZ', then=0),
                    When(country='', then=2),
                    default=1))

        for column in columns:
            if self.ordering == 'desc':
                rules.append('-' + column)
            else:
                rules.append(column)

        return queryset.order_by(*rules)


__all__ = ["ProfileListView"]
