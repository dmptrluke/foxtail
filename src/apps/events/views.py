from datetime import date, datetime

from django.db.models import Q
from django.http import Http404
from django.views.generic import DetailView, ListView
from django.views.generic.dates import YearMixin

from .models import Event


def _event_years():
    return Event.objects.dates('start', 'year', order='DESC').values_list('start__year', flat=True)


class EventListView(ListView):
    template_name = 'events/list.html'
    context_object_name = 'event_list'

    def get_queryset(self):
        return Event.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        upcoming_filter = Q(start__gte=today) | Q(end__gte=today)
        upcoming = Event.objects.filter(upcoming_filter).prefetch_related('tags').order_by('start')
        context['upcoming_events'] = upcoming
        context['past_events'] = Event.objects.exclude(upcoming_filter).prefetch_related('tags').order_by('-start')
        context['featured_event'] = upcoming.first()
        context['event_years'] = _event_years()
        return context


class EventListYearView(YearMixin, ListView):
    template_name = 'events/list.html'
    context_object_name = 'event_list'

    def get_queryset(self):
        return Event.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            year = datetime.strptime(str(self.get_year()), self.get_year_format()).year
        except ValueError:
            raise Http404() from None

        context['year'] = str(year)
        today = date.today()
        upcoming_filter = Q(start__gte=today) | Q(end__gte=today)
        year_qs = Event.objects.filter(start__year=year).prefetch_related('tags')
        context['upcoming_events'] = year_qs.filter(upcoming_filter).order_by('start')
        context['past_events'] = year_qs.exclude(upcoming_filter).order_by('-start')
        context['event_years'] = _event_years()
        return context


class EventDetailView(YearMixin, DetailView):
    model = Event
    template_name = 'events/detail.html'

    def get_queryset(self):
        try:
            date = datetime.strptime(str(self.get_year()), self.get_year_format())
        except ValueError:
            raise Http404() from None

        return Event.objects.filter(start__year=date.year, slug=self.kwargs['slug']).prefetch_related('tags')


__all__ = ['EventDetailView', 'EventListView', 'EventListYearView']
