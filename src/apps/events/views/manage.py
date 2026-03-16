from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from csp_helpers.mixins import CSPViewMixin

from apps.core.mixins import PermissionMixin

from ..models import Event
from ..tasks import geocode_event


class EventManageListView(PermissionMixin, ListView):
    permission_required = 'events.manage_events'
    model = Event
    template_name = 'events/manage/event_list.html'
    context_object_name = 'events'
    paginate_by = 20

    def get_queryset(self):
        return Event.objects.prefetch_related('tags').order_by('-start')


class _EventFormMixin:
    def _save_event(self, form, success_msg):
        self.object = form.save(commit=False)
        if 'address' in form.changed_data:
            self.object.latitude = None
            self.object.longitude = None
        self.object.save()
        form.save_m2m()
        self.object.tags.set(form.cleaned_data.get('tags', []))
        if self.object.address and 'address' in form.changed_data:
            transaction.on_commit(lambda: geocode_event(self.object.pk, self.object.address))
        messages.success(self.request, success_msg.format(title=self.object.title))
        return HttpResponseRedirect(reverse('events:event_edit', kwargs={'pk': self.object.pk}))


class EventCreateView(_EventFormMixin, CSPViewMixin, PermissionMixin, CreateView):
    permission_required = 'events.manage_events'
    model = Event
    template_name = 'events/manage/event_edit.html'

    def get_form_class(self):
        from ..forms import EventForm

        return EventForm

    def form_valid(self, form):
        return self._save_event(form, 'Event "{title}" created.')


class EventUpdateView(_EventFormMixin, CSPViewMixin, PermissionMixin, UpdateView):
    permission_required = 'events.manage_events'
    model = Event
    template_name = 'events/manage/event_edit.html'

    def get_form_class(self):
        from ..forms import EventForm

        return EventForm

    def form_valid(self, form):
        return self._save_event(form, 'Event "{title}" saved.')


class EventDeleteView(PermissionMixin, DeleteView):
    permission_required = 'events.manage_events'
    model = Event
    template_name = 'events/manage/event_delete.html'
    success_url = reverse_lazy('events:manage_list')

    def form_valid(self, form):
        title = self.object.title
        result = super().form_valid(form)
        messages.success(self.request, f'Event "{title}" deleted.')
        return result
