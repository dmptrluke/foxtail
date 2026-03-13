from django.core.exceptions import ValidationError

import pytest

from apps.organisations.tests.factories import EventSeriesFactory, OrganisationFactory

from ..models import Event
from .factories import EventFactory

pytestmark = pytest.mark.django_db


class TestEventQuerySetForOrganisation:
    # returns events with a direct organisation FK
    def test_direct_organisation(self):
        org = OrganisationFactory()
        event = EventFactory(organisation=org)
        EventFactory()
        assert list(Event.objects.for_organisation(org)) == [event]

    # returns events whose series has the organisation
    def test_via_series(self):
        org = OrganisationFactory()
        series = EventSeriesFactory(organisation=org)
        event = EventFactory(series=series)
        EventFactory()
        assert list(Event.objects.for_organisation(org)) == [event]

    # returns both direct and series-linked events without duplicates
    def test_combined(self):
        org = OrganisationFactory()
        series = EventSeriesFactory(organisation=org)
        direct_event = EventFactory(organisation=org)
        series_event = EventFactory(series=series)
        EventFactory()
        result = set(Event.objects.for_organisation(org))
        assert result == {direct_event, series_event}


class TestEventCleanOrganisation:
    # event in series-with-org cannot also have a direct org
    def test_series_with_org_and_direct_org_raises(self):
        org = OrganisationFactory()
        series = EventSeriesFactory(organisation=org)
        event = EventFactory.build(series=series, organisation=org)
        with pytest.raises(ValidationError, match='direct organisation'):
            event.clean()

    # event in series-with-org and no direct org is valid
    def test_series_with_org_no_direct_org_passes(self):
        org = OrganisationFactory()
        series = EventSeriesFactory(organisation=org)
        event = EventFactory.build(series=series, organisation=None)
        event.clean()

    # event with direct org and no series is valid
    def test_direct_org_no_series_passes(self):
        org = OrganisationFactory()
        event = EventFactory.build(organisation=org, series=None)
        event.clean()

    # event in series-without-org and a direct org is valid
    def test_series_without_org_and_direct_org_passes(self):
        org = OrganisationFactory()
        series = EventSeriesFactory(organisation=None)
        event = EventFactory.build(series=series, organisation=org)
        event.clean()


class TestEventResolvedOrganisation:
    # prefers series.organisation when both exist
    def test_from_series(self):
        org = OrganisationFactory()
        series = EventSeriesFactory(organisation=org)
        event = EventFactory.build(series=series, organisation=None)
        assert event.resolved_organisation == org

    # falls back to direct organisation when series has none
    def test_from_direct(self):
        org = OrganisationFactory()
        event = EventFactory.build(organisation=org, series=None)
        assert event.resolved_organisation == org

    # returns None when neither is set
    def test_none(self):
        event = EventFactory.build(organisation=None, series=None)
        assert event.resolved_organisation is None
