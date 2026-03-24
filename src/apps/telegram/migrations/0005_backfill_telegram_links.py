"""Create TelegramLink records for existing OAuth-linked Telegram SocialAccounts."""

from django.db import migrations


def backfill_telegram_links(apps, schema_editor):
    SocialAccount = apps.get_model('socialaccount', 'SocialAccount')
    TelegramLink = apps.get_model('telegram', 'TelegramLink')

    for sa in SocialAccount.objects.filter(provider='telegram').select_related('user'):
        id_token = sa.extra_data.get('id_token', {})
        telegram_id = int(id_token.get('id', 0))
        if not telegram_id:
            continue

        TelegramLink.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                'user': sa.user,
                'telegram_username': id_token.get('preferred_username', ''),
                'first_name': id_token.get('name', ''),
            },
        )

        # add top-level keys matching other providers so allauth's to_str() works
        sa.extra_data['username'] = id_token.get('preferred_username', '')
        sa.extra_data['name'] = id_token.get('name', '')
        sa.save(update_fields=['extra_data'])


class Migration(migrations.Migration):
    dependencies = [
        ('telegram', '0004_linktoken_first_name'),
        ('socialaccount', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(backfill_telegram_links, migrations.RunPython.noop),
    ]
