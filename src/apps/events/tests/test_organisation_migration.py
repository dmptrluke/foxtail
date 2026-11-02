from datetime import date

from django.db import connection
from django.db.migrations.executor import MigrationExecutor

import pytest


# ownership migration rejects unknown owners and supports upgrading, downgrading, and upgrading again
@pytest.mark.django_db(transaction=True)
def test_event_organisation_migration():
    before = [('events', '0020_eventtickettier'), ('organisations', '0011_add_manawatu_whanganui_region')]
    after = [('events', '0021_event_organisation')]
    executor = MigrationExecutor(connection)
    executor.migrate(before)
    apps = executor.loader.project_state(before).apps
    Organisation = apps.get_model('organisations', 'Organisation')
    EventSeries = apps.get_model('organisations', 'EventSeries')
    Event = apps.get_model('events', 'Event')

    try:
        direct_org = Organisation.objects.create(name='Direct', slug='direct')
        series_org = Organisation.objects.create(name='Series', slug='series')
        series = EventSeries.objects.create(name='Annual', slug='annual', organisation=series_org)
        unknown_series = EventSeries.objects.create(name='Unknown series', slug='unknown-series')
        direct_event = Event.objects.create(
            title='Direct', slug='direct', start=date(2026, 6, 1), organisation=direct_org
        )
        series_event = Event.objects.create(title='Series', slug='series', start=date(2026, 6, 1), series=series)
        conflicting_event = Event.objects.create(
            title='Both', slug='both', start=date(2026, 6, 1), series=series, organisation=direct_org
        )
        orphan = Event.objects.create(title='Unknown', slug='unknown', start=date(2026, 6, 1))

        with pytest.raises(RuntimeError, match='Assign an organisation to these event series'):
            MigrationExecutor(connection).migrate(after)
        unknown_series.organisation = direct_org
        unknown_series.save()

        with pytest.raises(RuntimeError, match='Assign an organisation to these events'):
            MigrationExecutor(connection).migrate(after)
        series_event.refresh_from_db()
        assert series_event.organisation_id is None

        orphan.delete()
        MigrationExecutor(connection).migrate(after)
        direct_event.refresh_from_db()
        series_event.refresh_from_db()
        conflicting_event.refresh_from_db()
        assert direct_event.organisation_id == direct_org.pk
        assert series_event.organisation_id == series_org.pk
        assert conflicting_event.organisation_id == series_org.pk
        assert series_event.age_requirement == ''

        MigrationExecutor(connection).migrate(before)
        direct_event.refresh_from_db()
        series_event.refresh_from_db()
        conflicting_event.refresh_from_db()
        assert direct_event.organisation_id == direct_org.pk
        assert series_event.organisation_id is None
        assert conflicting_event.organisation_id is None

        MigrationExecutor(connection).migrate(after)
        series_event.refresh_from_db()
        assert series_event.organisation_id == series_org.pk
    finally:
        EventSeries.objects.filter(organisation_id__isnull=True).delete()
        Event.objects.filter(organisation_id__isnull=True, series__organisation_id__isnull=True).delete()
        MigrationExecutor(connection).migrate(after)
