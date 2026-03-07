from django.db import migrations


def nulls_to_empty(apps, schema_editor):
    Event = apps.get_model('events', 'Event')
    Event.objects.filter(image__isnull=True).update(image='')


class Migration(migrations.Migration):
    dependencies = [
        ('events', '0009_switch_to_imagefield'),
    ]

    operations = [
        migrations.RunPython(nulls_to_empty, migrations.RunPython.noop),
    ]
