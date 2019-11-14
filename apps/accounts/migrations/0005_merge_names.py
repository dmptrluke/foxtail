from django.db import migrations


def combine_names(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    User = apps.get_model('accounts', 'User')
    for user in User.objects.all():
        user.full_name = ' '.join([user.first_name, user.last_name])
        user.save()


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0004_add_full_name'),
    ]

    operations = [
        migrations.RunPython(combine_names),
    ]
