from datetime import date, datetime

from django.db.models import Q
from django.http import Http404
from django.views.generic import DetailView, ListView
from django.views.generic.dates import YearMixin

from .models import Event


class EventList(ListView):
    template_name = 'event_list.html'
    context_object_name = 'event_list'

    def get_queryset(self):
        return Event.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        upcoming_filter = Q(start__gte=today) | Q(end__gte=today)
        context['upcoming_events'] = (
            Event.objects.filter(upcoming_filter)
            .prefetch_related('tags')
            .order_by('start')
        )
        context['past_events'] = (
            Event.objects.exclude(upcoming_filter)
            .prefetch_related('tags')
            .order_by('-start')
        )
        return context


class EventListYear(YearMixin, ListView):
    template_name = 'event_list.html'
    context_object_name = 'event_list'

    def get_queryset(self):
        return Event.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            year = datetime.strptime(str(self.get_year()), self.get_year_format()).year
        except ValueError:
            raise Http404()

        context['year'] = str(year)
        today = date.today()
        upcoming_filter = Q(start__gte=today) | Q(end__gte=today)
        year_qs = Event.objects.filter(start__year=year).prefetch_related('tags')
        context['upcoming_events'] = year_qs.filter(upcoming_filter).order_by('start')
        context['past_events'] = year_qs.exclude(upcoming_filter).order_by('-start')
        return context


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
