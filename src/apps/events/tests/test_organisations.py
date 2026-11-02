from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError

import pytest

from apps.organisations.tests.factories import EventSeriesFactory, OrganisationFactory

from .factories import EventFactory

pytestmark = pytest.mark.django_db


class TestEventCleanOrganisation:
    # a deleted or invalid series produces a validation error instead of a missing-object exception
    def test_invalid_series_is_reported(self):
        event = EventFactory.build(organisation=OrganisationFactory(), series_id=-1)
        with pytest.raises(ValidationError) as error:
            event.full_clean()
        assert 'series' in error.value.message_dict

    # date and ownership errors are reported together so editors can correct both
    def test_reports_all_custom_errors(self):
        series = EventSeriesFactory()
        event = EventFactory.build(organisation=OrganisationFactory(), series=series)
        event.end = event.start - timedelta(days=1)
        with pytest.raises(ValidationError) as error:
            event.clean()
        assert set(error.value.message_dict) == {'end', 'series'}

    # an event cannot use a series owned by a different organisation
    def test_mismatched_series_raises(self):
        org = OrganisationFactory()
        series = EventSeriesFactory(organisation=org)
        event = EventFactory.build(series=series, organisation=OrganisationFactory())
        with pytest.raises(ValidationError, match='series must belong'):
            event.clean()

    # an event and its series can share the same organisation
    def test_matching_series_passes(self):
        org = OrganisationFactory()
        series = EventSeriesFactory(organisation=org)
        event = EventFactory.build(series=series, organisation=org)
        event.clean()

    # event with direct org and no series is valid
    def test_direct_org_no_series_passes(self):
        org = OrganisationFactory()
        event = EventFactory.build(organisation=org, series=None)
        event.clean()

    # series require their own organisation even when they have no events
    def test_series_organisation_is_required(self):
        series = EventSeriesFactory.build(organisation=None)
        with pytest.raises(ValidationError) as error:
            series.full_clean()
        assert 'organisation' in error.value.message_dict

    # deleting an organisation cannot orphan an empty series
    def test_series_organisation_deletion_is_protected(self):
        series = EventSeriesFactory()
        with pytest.raises(ProtectedError):
            series.organisation.delete()

    # events require an organisation even when they have no series
    def test_organisation_is_required(self):
        event = EventFactory.build(organisation=None, series=None)
        with pytest.raises(ValidationError) as error:
            event.full_clean()
        assert 'organisation' in error.value.message_dict

    # deleting an organisation cannot orphan its events
    def test_organisation_deletion_is_protected(self):
        event = EventFactory()
        with pytest.raises(ProtectedError):
            event.organisation.delete()

    # a series cannot change owner while its events belong to another organisation
    def test_series_owner_change_is_blocked(self):
        org = OrganisationFactory()
        series = EventSeriesFactory(organisation=org)
        EventFactory(organisation=org, series=series)
        series.organisation = OrganisationFactory()
        with pytest.raises(ValidationError, match='must match all events'):
            series.clean()
