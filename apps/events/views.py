from django.views.generic import ListView, DetailView

from .models import Event


class EventList(ListView):
    model = Event
    template_name = 'event_list.html'


class EventDetail(DetailView):
    model = Event
    template_name = 'event_detail.html'


__all__ = ['EventList', 'EventDetail']
