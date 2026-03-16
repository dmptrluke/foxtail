from django.db import migrations, models

COUNTRY_MAP = {
    'New Zealand': 'NZ',
    'Australia': 'AU',
}


def convert_country_names_to_codes(apps, schema_editor):
    Organisation = apps.get_model('organisations', 'Organisation')
    for name, code in COUNTRY_MAP.items():
        Organisation.objects.filter(country=name).update(country=code)


def convert_country_codes_to_names(apps, schema_editor):
    Organisation = apps.get_model('organisations', 'Organisation')
    for name, code in COUNTRY_MAP.items():
        Organisation.objects.filter(country=code).update(country=name)


class Migration(migrations.Migration):
    dependencies = [
        ('organisations', '0005_organisation_type_region'),
    ]

    operations = [
        migrations.RunPython(convert_country_names_to_codes, convert_country_codes_to_names),
        migrations.AlterField(
            model_name='organisation',
            name='country',
            field=models.CharField(blank=True, choices=[('NZ', 'New Zealand'), ('AU', 'Australia')], max_length=2),
        ),
    ]
