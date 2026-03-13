from django.db.models import Q
from django.views.generic import DetailView

from published.utils import queryset_filter

from apps.blog.models import Post
from apps.events.models import Event

from .models import EventSeries, Organisation


class OrganisationDetailView(DetailView):
    model = Organisation
    template_name = 'organisations/organisation_detail.html'

    def get_queryset(self):
        return Organisation.objects.prefetch_related('series')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = self.object
        series = org.series.all()
        events = (
            queryset_filter(Event.objects.for_organisation(org))
            .select_related('organisation', 'series')
            .order_by('-start')
        )
        posts = (
            queryset_filter(Post.objects)
            .filter(Q(organisations=org) | Q(events__in=events) | Q(event_series__in=series))
            .distinct()
        )
        context['series'] = series
        context['events'] = events
        context['posts'] = posts
        return context


class EventSeriesDetailView(DetailView):
    model = EventSeries
    template_name = 'organisations/eventseries_detail.html'

    def get_queryset(self):
        return EventSeries.objects.select_related('organisation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        series = self.object
        events = queryset_filter(Event.objects).filter(series=series).order_by('-start')
        posts = queryset_filter(Post.objects).filter(Q(event_series=series) | Q(events__in=events)).distinct()
        context['events'] = events
        context['posts'] = posts
        return context
