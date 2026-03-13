from datetime import date

from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.views.generic.dates import YearMixin

from csp_helpers.mixins import CSPViewMixin
from published.mixins import PublishedDetailMixin
from published.utils import queryset_filter
from structured_data.views import StructuredDataMixin

from apps.core.mixins import PermissionMixin

from .models import Event


def _event_years():
    return queryset_filter(Event.objects).dates('start', 'year', order='DESC').values_list('start__year', flat=True)


class EventListView(StructuredDataMixin, ListView):
    template_name = 'events/list.html'
    context_object_name = 'event_list'

    def get_queryset(self):
        return Event.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        upcoming_filter = Q(start__gte=today) | Q(end__gte=today)
        published = queryset_filter(Event.objects, self.request.user)
        upcoming = published.filter(upcoming_filter).prefetch_related('tags').order_by('start')
        context['upcoming_events'] = upcoming
        context['past_events'] = published.exclude(upcoming_filter).prefetch_related('tags').order_by('-start')
        context['featured_event'] = upcoming.first()
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
        return Event.objects.filter(start__year=year, slug=self.kwargs['slug']).prefetch_related('tags')


# --- Management views ---


class EventManageListView(PermissionMixin, ListView):
    permission_required = 'events.manage_events'
    model = Event
    template_name = 'events/event_manage_list.html'
    context_object_name = 'events'
    paginate_by = 20

    def get_queryset(self):
        return Event.objects.prefetch_related('tags').order_by('-start')


class EventCreateView(CSPViewMixin, PermissionMixin, CreateView):
    permission_required = 'events.manage_events'
    model = Event
    template_name = 'events/event_form.html'

    def get_form_class(self):
        from .forms import EventForm

        return EventForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        _apply_geocoding(self.object, form.changed_data, self.request)
        self.object.save()
        form.save_m2m()
        self.object.tags.set(form.cleaned_data.get('tags', []))
        messages.success(self.request, f'Event "{self.object.title}" created.')
        return HttpResponseRedirect(reverse('events:event_edit', kwargs={'pk': self.object.pk}))


class EventUpdateView(CSPViewMixin, PermissionMixin, UpdateView):
    permission_required = 'events.manage_events'
    model = Event
    template_name = 'events/event_form.html'

    def get_form_class(self):
        from .forms import EventForm

        return EventForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        _apply_geocoding(self.object, form.changed_data, self.request)
        self.object.save()
        form.save_m2m()
        self.object.tags.set(form.cleaned_data.get('tags', []))
        messages.success(self.request, f'Event "{self.object.title}" saved.')
        return HttpResponseRedirect(reverse('events:event_edit', kwargs={'pk': self.object.pk}))


class EventDeleteView(PermissionMixin, DeleteView):
    permission_required = 'events.manage_events'
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('events:manage_list')

    def form_valid(self, form):
        title = self.object.title
        result = super().form_valid(form)
        messages.success(self.request, f'Event "{title}" deleted.')
        return result


def _apply_geocoding(obj, changed_data, request):
    api_key = getattr(settings, 'MAPTILER_API_KEY', None)
    if not api_key or 'address' not in changed_data:
        return
    if not obj.address:
        obj.latitude = None
        obj.longitude = None
        return
    from .maptiler import geocode

    coords = geocode(obj.address, api_key)
    if coords:
        obj.latitude, obj.longitude = coords
    else:
        messages.warning(request, 'Address could not be geocoded.')


__all__ = [
    'EventCreateView',
    'EventDeleteView',
    'EventDetailView',
    'EventListView',
    'EventListYearView',
    'EventManageListView',
    'EventUpdateView',
]
