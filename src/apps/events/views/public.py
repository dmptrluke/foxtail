from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.dates import YearMixin

from published.mixins import PublishedDetailMixin
from published.utils import queryset_filter
from structured_data.views import StructuredDataMixin

from apps.core.views import ApiView

from ..ics import generate_ics
from ..models import Event, EventInterest


def _event_years():
    result = cache.get('event_years')
    if result is None:
        result = list(
            queryset_filter(Event.objects).dates('start', 'year', order='DESC').values_list('start__year', flat=True)
        )
        cache.set('event_years', result, 3600)
    return result


class EventListView(StructuredDataMixin, ListView):
    template_name = 'events/list.html'
    context_object_name = 'event_list'

    def get_queryset(self):
        return Event.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        published = queryset_filter(Event.objects, self.request.user).with_relations().prefetch_related('tags')
        upcoming = list(published.not_ended().order_by('start'))
        context['upcoming_events'] = upcoming
        context['past_events'] = published.ended().order_by('-start')
        context['featured_event'] = upcoming[0] if upcoming else None
        context['event_years'] = _event_years()
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
        year_qs = (
            queryset_filter(Event.objects, self.request.user)
            .with_relations()
            .filter(start__year=year)
            .prefetch_related('tags')
        )
        context['upcoming_events'] = year_qs.not_ended().order_by('start')
        context['past_events'] = year_qs.ended().order_by('-start')
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
            Event.objects.filter(start__year=year, slug=self.kwargs['slug']).with_relations().prefetch_related('tags')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.blog.models import Post

        context['related_posts'] = list(
            queryset_filter(Post.objects).filter(events=self.object).link_fields().order_by('-created')
        )

        event = self.object
        org = event.resolved_organisation
        series = event.series
        show_series = bool(series)
        # Hide series when org has one series with the same name (redundant display).
        # Check name equality before count() to avoid the DB query when names differ.
        if (
            show_series
            and org
            and series.organisation_id == org.pk
            and series.name == org.name
            and org.series.count() == 1
        ):
            show_series = False
        context['show_series'] = show_series

        if self.request.user.is_authenticated:
            interest = EventInterest.objects.filter(event=self.object, user=self.request.user).first()
            context['user_interest_status'] = interest.status if interest else ''

        context['interests'] = list(self.object.interests.with_user_display()[:10])

        count_map = self.object.interests.status_counts()
        context['interest_count'] = sum(count_map.values())
        context['interested_count'] = count_map.get(EventInterest.INTERESTED, 0)
        context['going_count'] = count_map.get(EventInterest.GOING, 0)
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

        count_map = event.interests.status_counts()
        return self.success(
            {
                'status': status or None,
                'interested_count': count_map.get(EventInterest.INTERESTED, 0),
                'going_count': count_map.get(EventInterest.GOING, 0),
            }
        )


class EventICSView(View):
    def get(self, request, pk):
        event = get_object_or_404(queryset_filter(Event.objects), pk=pk)
        cal = generate_ics(event)
        response = HttpResponse(cal, content_type='text/calendar')
        response['Content-Disposition'] = f'attachment; filename="{event.slug}.ics"'
        return response
