# Generated by Django 3.0 on 2019-12-23 07:02

from django.db import migrations, models

import apps.directory.validators


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0002_defuck_everything'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='profile_URL',
            field=models.CharField(blank=True, max_length=25, null=True, unique=True, validators=[apps.directory.validators.URLValidator()]),
        ),
    ]
