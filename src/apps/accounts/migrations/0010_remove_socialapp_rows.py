from django.db import migrations


def remove_socialapp_rows(apps, schema_editor):
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    SocialApp.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0009_switch_to_imagefield'),
        ('socialaccount', '0006_alter_socialaccount_extra_data'),
    ]

    operations = [
        migrations.RunPython(remove_socialapp_rows, migrations.RunPython.noop),
    ]
