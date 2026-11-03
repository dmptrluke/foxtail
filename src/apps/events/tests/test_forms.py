import pytest
from published.constants import AVAILABLE

from apps.organisations.tests.factories import EventSeriesFactory, OrganisationFactory

from ..forms import EventForm
from ..models import Event

pytestmark = pytest.mark.django_db


class TestEventForm:
    # event editors can select a palette or clear it to restore visitor preferences
    @pytest.mark.parametrize('scheme', ['forest', 'twilight', 'contrast', ''])
    def test_saves_color_scheme(self, event, scheme):
        event.color_scheme = 'ocean'
        event.save()
        form = EventForm(
            instance=event,
            data={
                'title': event.title,
                'description': event.description,
                'organisation': event.organisation_id,
                'location': event.location,
                'start': event.start.isoformat(),
                'publish_status': event.publish_status,
                'image_ppoi': '0.5x0.5',
                'color_scheme': scheme,
            },
        )
        assert form.is_valid(), form.errors
        form.save()
        event.refresh_from_db()
        assert event.color_scheme == scheme

    # arbitrary class names cannot be submitted as event palettes
    def test_rejects_unknown_color_scheme(self):
        form = EventForm(data={'color_scheme': 'unknown'})
        assert not form.is_valid()
        assert 'color_scheme' in form.errors

    # the event editor offers only series owned by its selected organisation
    def test_series_choices_match_organisation(self, organisation):
        matching = EventSeriesFactory(organisation=organisation)
        EventSeriesFactory(organisation=OrganisationFactory())
        form = EventForm(prefix='event', initial={'organisation': organisation.pk})
        assert list(form.fields['series'].queryset) == [matching]
        assert form.fields['series'].widget.attrs['data-autocomplete-parent'] == 'id_event-organisation'

    # initial model instances are accepted as parent values just like initial primary keys
    def test_series_choices_accept_initial_organisation_instance(self, organisation):
        matching = EventSeriesFactory(organisation=organisation)
        form = EventForm(initial={'organisation': organisation})
        assert list(form.fields['series'].queryset) == [matching]

    # changing organisation on submission cannot retain a series belonging to another group
    def test_submitted_organisation_controls_series_choices(self):
        previous = EventSeriesFactory()
        organisation = OrganisationFactory()
        matching = EventSeriesFactory(organisation=organisation)
        form = EventForm(data={'organisation': organisation.pk, 'series': previous.pk})
        assert list(form.fields['series'].queryset) == [matching]
        assert not form.is_valid()
        assert 'series' in form.errors

    # an end date without a start produces a field error instead of crashing validation
    def test_end_date_without_start(self, organisation):
        form = EventForm(
            data={
                'title': 'Missing start',
                'description': 'Event description.',
                'organisation': organisation.pk,
                'location': 'Wellington',
                'end': '2026-06-15',
                'publish_status': AVAILABLE,
                'image_ppoi': '0.5x0.5',
            }
        )
        assert not form.is_valid()
        assert set(form.errors) == {'start'}

    # existing event's tags are loaded into the initial field
    def test_tags_loaded_on_edit(self, event: Event):
        event.tags.add('meetup', 'social')
        form = EventForm(instance=event)
        assert set(form['tags'].value()) == set(event.tags.all())

    # image_ppoi field is included (required for ProcessedImageField validation)
    def test_image_ppoi_in_fields(self):
        form = EventForm()
        assert 'image_ppoi' in form.fields
