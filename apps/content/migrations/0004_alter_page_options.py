# Generated by Django 4.2.15 on 2024-09-01 23:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0003_remove_fields'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='page',
            options={'verbose_name': 'page', 'verbose_name_plural': 'pages'},
        ),
    ]