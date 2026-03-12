from django.db import migrations


def create_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Event Editors')


def remove_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Event Editors').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('events', '0013_remove_map_image'),
    ]

    operations = [
        migrations.RunPython(create_group, remove_group),
    ]
