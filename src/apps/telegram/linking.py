"""Synchronize Telegram bot links and sign-in accounts"""

import logging

from django.db import IntegrityError, transaction

from allauth.socialaccount.models import SocialAccount

from .models import TelegramLink

logger = logging.getLogger(__name__)


def validate_link(user, telegram_id):
    """Reject links that would change an existing Telegram identity or owner"""
    # Either table may hold the only ownership record, so both must agree before a link is created.
    if TelegramLink.objects.filter(telegram_id=telegram_id).exclude(user=user).exists():
        raise IntegrityError('Telegram account is already linked to another user')
    if TelegramLink.objects.filter(user=user).exclude(telegram_id=telegram_id).exists():
        raise IntegrityError('User is already linked to another Telegram account')
    if SocialAccount.objects.filter(provider='telegram', uid=str(telegram_id)).exclude(user=user).exists():
        raise IntegrityError('Telegram sign-in account belongs to another user')
    # One sign-in identity per user keeps account connections consistent with the one-to-one bot link.
    if SocialAccount.objects.filter(user=user, provider='telegram').exclude(uid=str(telegram_id)).exists():
        raise IntegrityError('User already has another Telegram sign-in account')


@transaction.atomic
def link(user, telegram_id, username='', name=''):
    """Create or refresh a user's Telegram link and sign-in account"""
    validate_link(user, telegram_id)
    tg_link, created = TelegramLink.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            'user': user,
            'username': username,
            'name': name,
            'is_blocked': False,
        },
    )
    if tg_link.user_id != user.pk:
        raise IntegrityError('Telegram account is already linked to another user')
    if not created:
        tg_link.username = username
        tg_link.name = name
        tg_link.is_blocked = False
        tg_link.save(update_fields=['username', 'name', 'is_blocked'])

    extra_data = {'id': telegram_id}
    if username:
        extra_data['username'] = username
    if name:
        extra_data['name'] = name

    # OAuth claims belong to allauth; bot sync must not replace them or transfer the sign-in identity.
    social_account, _ = SocialAccount.objects.get_or_create(
        provider='telegram',
        uid=str(telegram_id),
        defaults={'user': user, 'extra_data': extra_data},
    )
    if social_account.user_id != user.pk:
        raise IntegrityError('Telegram sign-in account belongs to another user')

    action = 'created' if created else 'updated'
    logger.info('Telegram link %s for user %s (telegram_id=%s)', action, user.pk, telegram_id)
    return tg_link


@transaction.atomic
def unlink(telegram_id):
    """Delete both links for a Telegram ID and return whether a bot link existed"""
    tg_deleted, _ = TelegramLink.objects.filter(telegram_id=telegram_id).delete()
    sa_deleted, _ = SocialAccount.objects.filter(provider='telegram', uid=str(telegram_id)).delete()
    logger.info('Unlinked telegram_id=%s (links=%d, social=%d)', telegram_id, tg_deleted, sa_deleted)
    return tg_deleted > 0
