from django.db import migrations


def nulls_to_empty(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    Post.objects.filter(image__isnull=True).update(image='')


class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0011_switch_to_imagefield'),
    ]

    operations = [
        migrations.RunPython(nulls_to_empty, migrations.RunPython.noop),
    ]
