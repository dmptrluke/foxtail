from django.db import migrations


def create_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='verifiers')


def remove_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='verifiers').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0011_verification'),
    ]

    operations = [
        migrations.RunPython(create_group, remove_group),
    ]
