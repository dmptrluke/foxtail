"""Fix Telegram SocialAccount uids.

OAuth-linked accounts used the OIDC sub as uid. Standardize to the real
Telegram user ID (from id_token.id) and remove any duplicates created
by the uid mismatch.
"""

from django.db import migrations


def fix_telegram_uids(apps, schema_editor):
    SocialAccount = apps.get_model('socialaccount', 'SocialAccount')

    for sa in SocialAccount.objects.filter(provider='telegram'):
        id_token = sa.extra_data.get('id_token', {})
        telegram_id = id_token.get('id')
        if not telegram_id:
            continue

        tid = str(telegram_id)
        if sa.uid == tid:
            continue

        # another account already has the correct uid — merge data into it
        existing = SocialAccount.objects.filter(provider='telegram', uid=tid).first()
        if existing:
            existing.extra_data.update(sa.extra_data)
            existing.save(update_fields=['extra_data'])
            sa.delete()
            continue

        sa.uid = tid
        sa.extra_data.setdefault('username', id_token.get('preferred_username', ''))
        sa.extra_data.setdefault('name', id_token.get('name', ''))
        sa.save(update_fields=['uid', 'extra_data'])


class Migration(migrations.Migration):
    dependencies = [
        ('telegram', '0006_rename_fields'),
        ('socialaccount', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(fix_telegram_uids, migrations.RunPython.noop),
    ]
