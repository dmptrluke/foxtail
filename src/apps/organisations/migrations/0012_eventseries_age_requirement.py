import django.db.models.deletion
from django.db import migrations, models


def require_series_organisations(apps, schema_editor):
    """Reject series without an organisation before making ownership required"""
    series = apps.get_model('organisations', 'EventSeries').objects.using(schema_editor.connection.alias)
    missing = list(series.filter(organisation_id__isnull=True).values_list('pk', flat=True)[:20])
    if missing:
        raise RuntimeError(
            f'Assign an organisation to these event series before migrating (up to 20 IDs shown): {missing}'
        )


class Migration(migrations.Migration):
    dependencies = [
        ('organisations', '0011_add_manawatu_whanganui_region'),
    ]

    operations = [
        migrations.RunPython(require_series_organisations, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='eventseries',
            name='organisation',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, related_name='series', to='organisations.organisation'
            ),
        ),
        migrations.AddField(
            model_name='eventseries',
            name='age_requirement',
            field=models.CharField(
                blank=True,
                choices=[('', 'Unspecified'), ('all', 'All Ages'), ('13', '13+'), ('16', '16+'), ('18', '18+')],
                max_length=3,
            ),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='age_requirement',
            field=models.CharField(
                blank=True,
                choices=[('', 'Unspecified'), ('all', 'All Ages'), ('13', '13+'), ('16', '16+'), ('18', '18+')],
                max_length=3,
            ),
        ),
    ]
