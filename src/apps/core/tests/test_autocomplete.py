import json

from django.urls import reverse

import pytest

from apps.events.models import Event
from apps.events.tests.factories import EventFactory
from apps.organisations.tests.factories import EventSeriesFactory, OrganisationFactory

from ..autocomplete import AutocompleteView

pytestmark = pytest.mark.django_db


class TestAutocompleteView:
    # parent filtering runs before the result limit so unrelated choices cannot crowd out matches
    def test_filters_before_limiting(self, client, user):
        organisation = OrganisationFactory()
        EventSeriesFactory.create_batch(21, organisation=OrganisationFactory(), name='Another series')
        matching = EventSeriesFactory(organisation=organisation, name='Target series')
        client.force_login(user)
        response = client.get(reverse('autocomplete:event_series'), {'organisation': organisation.pk, 'q': 'series'})
        assert response.json()['results'] == [{'id': matching.pk, 'text': matching.name}]

    # invalid supplied parent values produce no choices instead of an unfiltered list
    @pytest.mark.parametrize('organisation', ['', 'invalid', '-1', '99999999999999999999999999'])
    def test_invalid_parent_has_no_results(self, client, user, organisation):
        EventSeriesFactory()
        client.force_login(user)
        response = client.get(reverse('autocomplete:event_series'), {'organisation': organisation})
        assert response.json()['results'] == []

    # independent selectors can search across parents by omitting the parent parameter
    def test_missing_parent_keeps_global_search(self, client, user):
        first = EventSeriesFactory(name='First match')
        second = EventSeriesFactory(name='Second match')
        EventSeriesFactory(name='Unrelated')
        client.force_login(user)
        response = client.get(reverse('autocomplete:event_series'), {'q': 'match'})
        assert {item['id'] for item in response.json()['results']} == {first.pk, second.pk}

    # the configured relation controls filtering rather than assuming an organisation parent
    def test_different_parent_field(self, user, request_factory):
        series = EventSeriesFactory()
        matching = EventFactory(series=series, organisation=series.organisation)
        EventFactory()
        request = request_factory.get('/', {'series': series.pk})
        request.user = user
        view = AutocompleteView.as_view(model=Event, search_fields=['title'], parent_field='series')
        response = view(request)
        assert json.loads(response.content)['results'] == [{'id': matching.pk, 'text': matching.title}]

    # an explicitly empty parent does not select rows with a null parent relationship
    def test_empty_parent_excludes_unparented_choices(self, user, request_factory):
        EventFactory(series=None)
        request = request_factory.get('/', {'series': ''})
        request.user = user
        view = AutocompleteView.as_view(model=Event, search_fields=['title'], parent_field='series')
        assert json.loads(view(request).content)['results'] == []

    # clients cannot turn arbitrary request parameters into relation filters
    def test_unconfigured_parent_is_ignored(self, client, user):
        first = EventFactory(title='First match')
        second = EventFactory(title='Second match')
        EventFactory(title='Unrelated')
        client.force_login(user)
        response = client.get(
            reverse('autocomplete:event'),
            {'q': 'match', 'organisation': first.organisation_id, 'parent_field': 'organisation'},
        )
        assert {item['id'] for item in response.json()['results']} == {first.pk, second.pk}
