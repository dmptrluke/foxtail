import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.middleware import LoggingMiddleware, SyncUserDataMiddleware
from bot.routers import commands, link, ping

bot = Bot(
    token=os.environ['TELEGRAM_BOT_TOKEN'],
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()

dp.update.outer_middleware(LoggingMiddleware())
dp.message.outer_middleware(SyncUserDataMiddleware())

dp.include_routers(
    link.router,
    commands.router,
    ping.router,
)
