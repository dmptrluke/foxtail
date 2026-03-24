import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from apps.telegram.models import TelegramLink

logger = logging.getLogger(__name__)

router = Router(name='commands')


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Kia ora! I'm the furry.nz bot.\n\n"
        'Use /link to connect your Telegram account to your furry.nz profile.\n'
        'Use /help to see all available commands.',
    )


@router.message(Command('status'))
async def cmd_status(message: Message):
    telegram_id = message.from_user.id
    try:
        link = await TelegramLink.objects.select_related('user').aget(telegram_id=telegram_id)
        await message.answer(
            f'Linked to <b>{link.user.username}</b> since {link.linked_at.strftime("%d %b %Y")}.',
        )
    except TelegramLink.DoesNotExist:
        await message.answer('Your Telegram account is not linked. Use /link to get started.')
    except Exception:
        logger.exception('Error checking status for %s', telegram_id)
        await message.answer('Something went wrong. Please try again later.')


@router.message(Command('unlink'))
async def cmd_unlink(message: Message):
    telegram_id = message.from_user.id
    try:
        from apps.telegram import linking

        deleted = await linking.aunlink(telegram_id)
        if deleted:
            await message.answer('Your account has been unlinked.')
        else:
            await message.answer('Your Telegram account is not linked.')
    except Exception:
        logger.exception('Error unlinking %s', telegram_id)
        await message.answer('Something went wrong. Please try again later.')


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(
        '<b>Available commands:</b>\n\n'
        '/link - Link your Telegram account to furry.nz\n'
        '/status - Check your link status\n'
        '/unlink - Remove your account link\n'
        '/ping - Check if the bot is running\n'
        '/help - Show this message',
    )
