from django.views.generic import ArchiveIndexView, DetailView, YearArchiveView

from .models import Event


class EventList(ArchiveIndexView):
    queryset = Event.objects.all().prefetch_related('tags')
    ordering = 'start'
    date_field = "start"
    make_object_list = True
    allow_future = True
    template_name = 'event_list.html'


class EventListYear(YearArchiveView):
    queryset = Event.objects.all().prefetch_related('tags')
    ordering = 'start'
    date_field = "start"
    make_object_list = True
    allow_future = True
    template_name = 'event_list.html'


class EventDetail(DetailView):
    model = Event
    template_name = 'event_detail.html'


__all__ = ['EventList', 'EventDetail']
