import django.db.models.deletion
from django.db import migrations, models
from django.db.models import OuterRef, Subquery


def populate_event_organisations(apps, schema_editor):
    """Copy series ownership onto events and reject events without an organisation"""
    db = schema_editor.connection.alias
    events = apps.get_model('events', 'Event').objects.using(db)
    series = apps.get_model('organisations', 'EventSeries').objects.using(db)
    missing = list(
        events.filter(organisation_id__isnull=True, series__organisation_id__isnull=True).values_list('pk', flat=True)[
            :20
        ]
    )
    if missing:
        raise RuntimeError(f'Assign an organisation to these events before migrating (up to 20 IDs shown): {missing}')
    owner = series.filter(pk=OuterRef('series_id')).order_by().values('organisation_id')[:1]
    events.filter(series__organisation_id__isnull=False).update(organisation_id=Subquery(owner))


def restore_series_ownership(apps, schema_editor):
    """Restore the series-only ownership representation for events in owned series"""
    events = apps.get_model('events', 'Event').objects.using(schema_editor.connection.alias)
    events.filter(series__organisation_id__isnull=False).update(organisation_id=None)


class Migration(migrations.Migration):
    dependencies = [
        ('events', '0020_eventtickettier'),
        ('organisations', '0012_eventseries_age_requirement'),
    ]

    operations = [
        migrations.RunPython(populate_event_organisations, restore_series_ownership),
        migrations.AlterField(
            model_name='event',
            name='organisation',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, related_name='events', to='organisations.organisation'
            ),
        ),
        migrations.AlterField(
            model_name='event',
            name='series',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='events',
                to='organisations.eventseries',
            ),
        ),
        migrations.AlterField(
            model_name='event',
            name='age_requirement',
            field=models.CharField(
                blank=True,
                choices=[('', 'Unspecified'), ('all', 'All Ages'), ('13', '13+'), ('16', '16+'), ('18', '18+')],
                max_length=3,
            ),
        ),
    ]
