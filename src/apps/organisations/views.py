from datetime import date

from django.db.models import F, Q
from django.views.generic import DetailView

from published.utils import queryset_filter

from apps.blog.models import Post
from apps.events.models import Event

from .models import EventSeries, Organisation


class OrganisationDetailView(DetailView):
    model = Organisation
    template_name = 'organisations/organisation_detail.html'

    def get_queryset(self):
        return Organisation.objects.prefetch_related('series', 'social_links')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = self.object
        series = org.series.all()
        social_links = org.social_links.all()
        events = (
            queryset_filter(Event.objects.for_organisation(org))
            .select_related('organisation', 'series')
            .order_by(F('series__name').asc(nulls_last=True), '-start')
        )
        posts = (
            queryset_filter(Post.objects)
            .filter(Q(organisations=org) | Q(events__in=events) | Q(event_series__in=series))
            .distinct()
        )
        next_event = (
            queryset_filter(Event.objects.for_organisation(org))
            .filter(Q(end__gte=date.today()) | Q(end__isnull=True, start__gte=date.today()))
            .select_related('series')
            .order_by('start')
            .first()
        )
        context['series'] = series
        context['social_links'] = social_links
        context['events'] = events
        context['posts'] = posts
        context['next_event'] = next_event
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
