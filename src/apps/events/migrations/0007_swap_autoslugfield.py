from django.db import migrations

from apps.core.fields import AutoSlugField


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_event_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='slug',
            field=AutoSlugField(populate_from='title', unique_for_year='start'),
        ),
    ]
