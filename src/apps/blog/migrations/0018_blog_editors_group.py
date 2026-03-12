from django.db import migrations


def create_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Blog Editors')


def remove_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Blog Editors').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('foxtail_blog', '0017_imagefield_deconstruct'),
    ]

    operations = [
        migrations.RunPython(create_group, remove_group),
    ]
