from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('events', '0010_image_null_to_empty'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='image',
            field=models.ImageField(blank=True, height_field='image_height', upload_to='events', width_field='image_width'),
        ),
    ]
