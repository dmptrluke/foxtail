from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foxtail_blog', '0015_migrate_author_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='author_legacy',
        ),
    ]
