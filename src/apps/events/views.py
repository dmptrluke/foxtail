from datetime import date, datetime

from django.conf import settings
from django.contrib import messages
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.views.generic.dates import YearMixin

from csp_helpers.mixins import CSPViewMixin
from published.mixins import PublishedDetailMixin
from published.utils import queryset_filter

from apps.core.mixins import PermissionMixin

from .models import Event


def _event_years():
    return queryset_filter(Event.objects).dates('start', 'year', order='DESC').values_list('start__year', flat=True)


class EventListView(ListView):
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
        year_qs = queryset_filter(Event.objects, self.request.user).filter(start__year=year).prefetch_related('tags')
        context['upcoming_events'] = year_qs.filter(upcoming_filter).order_by('start')
        context['past_events'] = year_qs.exclude(upcoming_filter).order_by('-start')
        context['event_years'] = _event_years()
        return context


class EventDetailView(PublishedDetailMixin, YearMixin, DetailView):
    model = Event
    template_name = 'events/detail.html'

    def get_queryset(self):
        try:
            date = datetime.strptime(str(self.get_year()), self.get_year_format())
        except ValueError:
            raise Http404() from None

        return Event.objects.filter(start__year=date.year, slug=self.kwargs['slug']).prefetch_related('tags')


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
        self.object = form.save()
        self.object.tags.set(form.cleaned_data.get('tags', []))
        _apply_geocoding(self.object, form.changed_data, self.request)
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
        self.object = form.save()
        self.object.tags.set(form.cleaned_data.get('tags', []))
        _apply_geocoding(self.object, form.changed_data, self.request)
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
    token = getattr(settings, 'MAPBOX_ACCESS_TOKEN', None)
    if not token or 'address' not in changed_data:
        return
    if obj.address:
        from .mapbox import geocode, static_map

        coords = geocode(obj.address, token)
        if coords:
            obj.latitude, obj.longitude = coords
            map_bytes = static_map(obj.latitude, obj.longitude, token)
            if map_bytes:
                filename = f'{obj.slug or "event"}-map.png'
                if obj.map_image:
                    obj.map_image.delete(save=False)
                obj.map_image.save(filename, ContentFile(map_bytes), save=False)
            obj.save()
        else:
            messages.warning(request, 'Address could not be geocoded.')
    else:
        obj.latitude = None
        obj.longitude = None
        if obj.map_image:
            obj.map_image.delete(save=False)
        obj.save()


__all__ = [
    'EventCreateView',
    'EventDeleteView',
    'EventDetailView',
    'EventListView',
    'EventListYearView',
    'EventManageListView',
    'EventUpdateView',
]
