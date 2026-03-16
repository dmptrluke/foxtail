from datetime import date

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView
from django.views.generic.dates import YearMixin

from published.mixins import PublishedDetailMixin
from published.utils import queryset_filter
from structured_data.views import StructuredDataMixin

from apps.core.views import ApiView
from apps.organisations.models import Organisation

from ..models import Event, EventInterest


def _event_years():
    return queryset_filter(Event.objects).dates('start', 'year', order='DESC').values_list('start__year', flat=True)


class EventListView(StructuredDataMixin, ListView):
    template_name = 'events/list.html'
    context_object_name = 'event_list'

    def get_queryset(self):
        return Event.objects.none()

    def _get_base_queryset(self):
        qs = queryset_filter(Event.objects, self.request.user).select_related('organisation', 'series')
        org_slug = self.request.GET.get('org')
        if org_slug:
            try:
                org = Organisation.objects.get(slug=org_slug)
                qs = qs.for_organisation(org)
                self._filter_org = org
            except Organisation.DoesNotExist:
                pass
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        upcoming_filter = Q(start__gte=today) | Q(end__gte=today)
        published = self._get_base_queryset()
        upcoming = published.filter(upcoming_filter).prefetch_related('tags').order_by('start')
        context['upcoming_events'] = upcoming
        context['past_events'] = published.exclude(upcoming_filter).prefetch_related('tags').order_by('-start')
        context['featured_event'] = upcoming.first()
        context['event_years'] = _event_years()
        context['filter_org'] = getattr(self, '_filter_org', None)
        return context

    def get_structured_data(self):
        return {
            '@type': 'CollectionPage',
            'name': 'Furry Events',
            'description': 'Furry conventions, meets, and community gatherings across New Zealand and beyond',
            'url': self.request.build_absolute_uri(),
        }


class EventListYearView(StructuredDataMixin, YearMixin, ListView):
    template_name = 'events/list.html'
    context_object_name = 'event_list'

    def get_queryset(self):
        return Event.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = int(self.get_year())

        context['year'] = str(year)
        today = date.today()
        upcoming_filter = Q(start__gte=today) | Q(end__gte=today)
        year_qs = queryset_filter(Event.objects, self.request.user).filter(start__year=year).prefetch_related('tags')
        context['upcoming_events'] = year_qs.filter(upcoming_filter).order_by('start')
        context['past_events'] = year_qs.exclude(upcoming_filter).order_by('-start')
        context['event_years'] = _event_years()
        return context

    def get_structured_data(self):
        year = self.get_year()
        return {
            '@type': 'CollectionPage',
            'name': f'Events in {year}',
            'description': f'Furry conventions and community events from {year}',
            'url': self.request.build_absolute_uri(),
        }


class EventDetailView(PublishedDetailMixin, YearMixin, DetailView):
    model = Event
    template_name = 'events/detail.html'

    def get_queryset(self):
        year = int(self.get_year())
        return (
            Event.objects.filter(start__year=year, slug=self.kwargs['slug'])
            .select_related('organisation', 'series', 'series__organisation')
            .prefetch_related('tags')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.blog.models import Post

        context['related_posts'] = queryset_filter(Post.objects).filter(events=self.object)

        event = self.object
        org = event.resolved_organisation
        series = event.series
        show_series = bool(series)
        if (
            show_series
            and org
            and series.organisation_id == org.pk
            and org.series.count() == 1
            and series.name == org.name
        ):
            show_series = False
        context['show_series'] = show_series
        return context


class EventInterestToggleView(ApiView):
    VALID_STATUSES = {EventInterest.INTERESTED, EventInterest.GOING}

    def post(self, request, pk):
        event = get_object_or_404(queryset_filter(Event.objects), pk=pk)
        status = self.data.get('status')

        if status and status not in self.VALID_STATUSES:
            return self.error('Invalid status')

        if status:
            EventInterest.objects.update_or_create(event=event, user=request.user, defaults={'status': status})
        else:
            EventInterest.objects.filter(event=event, user=request.user).delete()

        counts = event.interests.values('status').annotate(n=Count('pk'))
        count_map = {r['status']: r['n'] for r in counts}
        return self.success(
            {
                'status': status or None,
                'interested_count': count_map.get(EventInterest.INTERESTED, 0),
                'going_count': count_map.get(EventInterest.GOING, 0),
            }
        )
