import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from apps.telegram.models import TelegramLink

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        start = time.monotonic()
        try:
            result = await handler(event, data)
            elapsed = (time.monotonic() - start) * 1000
            logger.info('Update processed in %.1fms', elapsed)
            return result
        except Exception:
            elapsed = (time.monotonic() - start) * 1000
            logger.exception('Handler error after %.1fms', elapsed)
            raise


class SyncUserDataMiddleware(BaseMiddleware):
    """Update TelegramLink fields from message.from_user on each interaction."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            user = event.from_user
            await TelegramLink.objects.filter(telegram_id=user.id).aupdate(
                telegram_username=user.username or '',
                first_name=user.first_name or '',
            )
        return await handler(event, data)
