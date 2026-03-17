from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_seed_site_settings'),
    ]

    operations = [
        migrations.RunSQL(
            'DROP TABLE IF EXISTS socialaccount_socialapp_sites',
            migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            'DROP TABLE IF EXISTS django_site',
            migrations.RunSQL.noop,
        ),
    ]
