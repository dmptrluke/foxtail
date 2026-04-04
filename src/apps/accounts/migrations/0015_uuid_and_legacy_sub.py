import uuid

from django.db import migrations, models


def backfill_uuids(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    for user in User.objects.filter(uuid__isnull=True):
        user.uuid = uuid.uuid4()
        user.save(update_fields=['uuid'])


def set_existing_clients_legacy(apps, schema_editor):
    ClientMetadata = apps.get_model('accounts', 'ClientMetadata')
    ClientMetadata.objects.update(legacy_sub=True)


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0014_alter_user_avatar'),
    ]

    operations = [
        # add uuid as nullable with no default so existing rows get NULL
        migrations.AddField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(backfill_uuids, migrations.RunPython.noop),
        # now make it non-nullable, unique, with default for future inserts
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name='clientmetadata',
            name='legacy_sub',
            field=models.BooleanField(
                default=False,
                help_text='Use sequential user ID as the OIDC sub claim instead of UUID.',
            ),
        ),
        migrations.RunPython(set_existing_clients_legacy, migrations.RunPython.noop),
    ]
