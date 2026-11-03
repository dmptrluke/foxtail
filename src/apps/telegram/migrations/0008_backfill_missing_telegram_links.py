import logging

from django.db import migrations

logger = logging.getLogger(__name__)


def backfill_links(apps, schema_editor):
    """Backfill unambiguous bot links from existing Telegram sign-in accounts"""
    SocialAccount = apps.get_model('socialaccount', 'SocialAccount')
    TelegramLink = apps.get_model('telegram', 'TelegramLink')
    database = schema_editor.connection.alias
    accounts = SocialAccount.objects.using(database).filter(provider='telegram')
    links = TelegramLink.objects.using(database)
    created = 0
    skipped = 0

    for account in accounts.iterator():
        try:
            telegram_id = int(account.uid)
        except (TypeError, ValueError):
            skipped += 1
            logger.warning('Skipping Telegram social account %s with a non-numeric UID', account.pk)
            continue
        if not 0 < telegram_id <= 2**63 - 1 or account.uid != str(telegram_id):
            skipped += 1
            logger.warning('Skipping Telegram social account %s with an invalid Telegram ID', account.pk)
            continue
        if links.filter(user_id=account.user_id, telegram_id=telegram_id).exists():
            continue

        # Multiple sign-in identities or conflicting links need an explicit ownership decision.
        if (
            accounts.filter(user_id=account.user_id).exclude(pk=account.pk).exists()
            or links.filter(user_id=account.user_id).exists()
            or links.filter(telegram_id=telegram_id).exists()
        ):
            skipped += 1
            logger.warning('Skipping conflicting Telegram social account %s for user %s', account.pk, account.user_id)
            continue

        extra = account.extra_data if isinstance(account.extra_data, dict) else {}
        data = extra.get('userinfo') or extra.get('id_token') or extra
        if not isinstance(data, dict):
            data = extra

        claim_id = data.get('id', extra.get('id'))
        if claim_id is not None and str(claim_id) != account.uid:
            skipped += 1
            logger.warning('Skipping Telegram social account %s with conflicting identity claims', account.pk)
            continue
        username = data.get('preferred_username') or extra.get('username') or ''
        name = data.get('name') or extra.get('name') or ''
        links.create(
            user_id=account.user_id,
            telegram_id=telegram_id,
            username=username[:32] if isinstance(username, str) else '',
            name=name[:64] if isinstance(name, str) else '',
        )
        created += 1

    logger.info('Backfilled %s Telegram links; skipped %s invalid or conflicting accounts', created, skipped)


class Migration(migrations.Migration):
    dependencies = [
        ('socialaccount', '0006_alter_socialaccount_extra_data'),
        ('telegram', '0001_initial_squashed_0007_fix_socialaccount_uids'),
    ]

    # Rollbacks must not delete repaired links that users may already have used.
    operations = [migrations.RunPython(backfill_links, migrations.RunPython.noop)]
