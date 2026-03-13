from django.views.generic import DetailView

from .models import EventSeries, Organisation


class OrganisationDetailView(DetailView):
    model = Organisation
    template_name = 'organisations/organisation_detail.html'


class EventSeriesDetailView(DetailView):
    model = EventSeries
    template_name = 'organisations/eventseries_detail.html'
