from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_swap_autoslugfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='map_image',
            field=models.ImageField(blank=True, upload_to='events/maps'),
        ),
    ]
