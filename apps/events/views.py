from datetime import datetime

from django.http import Http404
from django.views.generic import DetailView, ListView
from django.views.generic.dates import YearMixin

from .models import Event


class EventList(ListView):
    queryset = Event.objects.all().prefetch_related('tags')
    ordering = 'start'
    template_name = 'event_list.html'
    context_object_name = 'event_list'


class EventListYear(YearMixin, ListView):
    ordering = 'start'
    template_name = 'event_list.html'
    context_object_name = 'event_list'

    def get_queryset(self):
        try:
            date = datetime.strptime(str(self.get_year()), self.get_year_format())
        except ValueError:
            raise Http404()

        return Event.objects.filter(
            start__year=date.year
        ).prefetch_related('tags')


class EventDetail(YearMixin, DetailView):
    model = Event
    template_name = 'event_detail.html'

    def get_queryset(self):
        try:
            date = datetime.strptime(str(self.get_year()), self.get_year_format())
        except ValueError:
            raise Http404()

        return Event.objects.filter(
            start__year=date.year,
            slug=self.kwargs['slug']
        )


__all__ = ['EventList', 'EventDetail']
