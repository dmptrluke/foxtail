# Generated by Django 3.0.2 on 2020-01-20 13:06

from django.db import migrations

import apps.directory.fields


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0005_privacy_rules'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='character',
            name='privacy_rules',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='privacy_rules',
        ),
        migrations.AddField(
            model_name='profile',
            name='description_privacy',
            field=apps.directory.fields.PrivacyField(),
        ),
    ]
