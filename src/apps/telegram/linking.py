"""Centralized TelegramLink + SocialAccount sync."""

import logging

from allauth.socialaccount.models import SocialAccount

from .models import TelegramLink

logger = logging.getLogger(__name__)


def link(user, telegram_id, username='', name=''):
    """Create or update TelegramLink and SocialAccount for a user."""
    tg_link, created = TelegramLink.objects.update_or_create(
        telegram_id=telegram_id,
        defaults={
            'user': user,
            'username': username,
            'name': name,
            'is_blocked': False,
        },
    )

    extra_data = {'id': telegram_id}
    if username:
        extra_data['username'] = username
    if name:
        extra_data['name'] = name

    SocialAccount.objects.update_or_create(
        provider='telegram',
        uid=str(telegram_id),
        defaults={'user': user, 'extra_data': extra_data},
    )

    action = 'created' if created else 'updated'
    logger.info('Telegram link %s for user %s (telegram_id=%s)', action, user.pk, telegram_id)
    return tg_link


def unlink(telegram_id):
    """Delete TelegramLink and SocialAccount by Telegram user ID."""
    tg_deleted, _ = TelegramLink.objects.filter(telegram_id=telegram_id).delete()
    sa_deleted, _ = SocialAccount.objects.filter(provider='telegram', uid=str(telegram_id)).delete()
    logger.info('Unlinked telegram_id=%s (links=%d, social=%d)', telegram_id, tg_deleted, sa_deleted)
    return tg_deleted > 0
