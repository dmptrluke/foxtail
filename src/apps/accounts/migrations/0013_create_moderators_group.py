from django.db import migrations


def create_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Moderators')


def remove_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Moderators').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0012_create_verifiers_group'),
    ]

    operations = [
        migrations.RunPython(create_group, remove_group),
    ]
