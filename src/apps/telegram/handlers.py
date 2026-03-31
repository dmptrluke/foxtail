"""Telegram bot command handlers. Each function receives chat_id, chat_type, and from_user."""

import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils.timezone import now

from . import api, linking
from .models import LinkToken, TelegramLink

logger = logging.getLogger(__name__)


def cmd_start(chat_id, chat_type, from_user):
    api.send_message(
        chat_id,
        "Kia ora! I'm the furry.nz bot.\n\n"
        'Use /link to connect your Telegram account to your furry.nz profile.\n'
        'Use /help to see all available commands.',
    )


def cmd_link(chat_id, chat_type, from_user):
    if chat_type != 'private':
        api.send_message(chat_id, 'This command only works in private chat.')
        return

    telegram_id = from_user['id']
    username = from_user.get('username', '')
    name = f'{from_user.get("first_name", "")} {from_user.get("last_name", "")}'.strip()

    try:
        if TelegramLink.objects.filter(telegram_id=telegram_id).exists():
            api.send_message(
                chat_id, 'Your Telegram account is already linked. Use /status to check or /unlink to remove it.'
            )
            return

        LinkToken.objects.filter(telegram_id=telegram_id).delete()
        token = secrets.token_urlsafe(48)
        LinkToken.objects.create(
            telegram_id=telegram_id,
            username=username,
            name=name,
            token=token,
            expires_at=now() + timedelta(minutes=15),
        )

        site_url = settings.SITE_URL.rstrip('/')
        api.send_message(
            chat_id,
            f'Open this link while logged in to furry.nz to connect your account:\n\n'
            f'{site_url}/accounts/link-telegram/{token}/\n\n'
            f'This link expires in 15 minutes.',
        )
    except Exception:
        logger.exception('Error creating link token for %s', telegram_id)
        api.send_message(chat_id, 'Something went wrong. Please try again later.')


def cmd_status(chat_id, chat_type, from_user):
    telegram_id = from_user['id']
    try:
        link = TelegramLink.objects.select_related('user').get(telegram_id=telegram_id)
        api.send_message(
            chat_id,
            f'Linked to <b>{link.user.username}</b> since {link.linked_at.strftime("%d %b %Y")}.',
        )
    except TelegramLink.DoesNotExist:
        api.send_message(chat_id, 'Your Telegram account is not linked. Use /link to get started.')
    except Exception:
        logger.exception('Error checking status for %s', telegram_id)
        api.send_message(chat_id, 'Something went wrong. Please try again later.')


def cmd_unlink(chat_id, chat_type, from_user):
    telegram_id = from_user['id']
    try:
        deleted = linking.unlink(telegram_id)
        if deleted:
            api.send_message(chat_id, 'Your account has been unlinked.')
        else:
            api.send_message(chat_id, 'Your Telegram account is not linked.')
    except Exception:
        logger.exception('Error unlinking %s', telegram_id)
        api.send_message(chat_id, 'Something went wrong. Please try again later.')


def cmd_help(chat_id, chat_type, from_user):
    api.send_message(
        chat_id,
        '<b>Available commands:</b>\n\n'
        '/link - Link your Telegram account to furry.nz\n'
        '/status - Check your link status\n'
        '/unlink - Remove your account link\n'
        '/ping - Check if the bot is running\n'
        '/help - Show this message',
    )


def cmd_ping(chat_id, chat_type, from_user):
    api.send_message(chat_id, 'pong')
