from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0012_image_null_to_empty'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, height_field='image_height', upload_to='blog', width_field='image_width'),
        ),
    ]
