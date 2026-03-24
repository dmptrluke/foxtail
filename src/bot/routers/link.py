import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils.timezone import now

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from apps.telegram.models import LinkToken, TelegramLink

logger = logging.getLogger(__name__)

router = Router(name='link')

SITE_URL = settings.SITE_URL.rstrip('/')


@router.message(Command('link'))
async def cmd_link(message: Message):
    if message.chat.type != 'private':
        await message.answer('This command only works in private chat.')
        return

    telegram_id = message.from_user.id
    telegram_username = message.from_user.username or ''
    first_name = message.from_user.first_name or ''

    try:
        if await TelegramLink.objects.filter(telegram_id=telegram_id).aexists():
            await message.answer(
                'Your Telegram account is already linked. Use /status to check or /unlink to remove it.'
            )
            return

        await LinkToken.objects.filter(telegram_id=telegram_id).adelete()

        token = secrets.token_urlsafe(48)
        await LinkToken.objects.acreate(
            telegram_id=telegram_id,
            telegram_username=telegram_username,
            first_name=first_name,
            token=token,
            expires_at=now() + timedelta(minutes=15),
        )

        link_url = f'{SITE_URL}/accounts/link-telegram/{token}/'
        await message.answer(
            f'Open this link while logged in to furry.nz to connect your account:\n\n{link_url}\n\n'
            f'This link expires in 15 minutes.',
        )
    except Exception:
        logger.exception('Error creating link token for %s', telegram_id)
        await message.answer('Something went wrong. Please try again later.')
