from django.urls import path

from taggit.models import Tag

from apps.core.autocomplete import AutocompleteView
from apps.events.models import Event
from apps.organisations.models import EventSeries, Organisation

app_name = 'autocomplete'

urlpatterns = [
    path('organisations/', AutocompleteView.as_view(model=Organisation, search_fields=['name']), name='organisation'),
    path('series/', AutocompleteView.as_view(model=EventSeries, search_fields=['name']), name='event_series'),
    path('events/', AutocompleteView.as_view(model=Event, search_fields=['title']), name='event'),
    path('tags/', AutocompleteView.as_view(model=Tag, search_fields=['name']), name='tag'),
]
