import asyncio
import logging
import os
import signal
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')

import django

django.setup()

from django.conf import settings  # noqa: E402

from bot.action_handlers import ACTION_HANDLERS  # noqa: E402
from bot.dispatcher import bot, dp  # noqa: E402
from bot.listener import ActionListener  # noqa: E402

logger = logging.getLogger(__name__)


def main(poll=False):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    )

    async def _run():
        shutdown_event = asyncio.Event()
        loop = asyncio.get_running_loop()

        def _handle_signal():
            logger.info('Received shutdown signal')
            shutdown_event.set()

        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, _handle_signal)

        from aiogram.types import BotCommand

        await bot.set_my_commands(
            [
                BotCommand(command='link', description='Link your Telegram account to furry.nz'),
                BotCommand(command='status', description='Check your link status'),
                BotCommand(command='unlink', description='Remove your account link'),
                BotCommand(command='ping', description='Check if the bot is running'),
                BotCommand(command='help', description='Show available commands'),
            ]
        )
        logger.info('Registered bot commands')

        listener = ActionListener(bot, ACTION_HANDLERS, settings.REDIS_URL)

        tasks = [
            listener.run(),
        ]

        if poll:
            logger.info('Starting bot with long polling')
            await bot.delete_webhook(drop_pending_updates=True)
            tasks.append(dp.start_polling(bot))
        else:
            from aiogram.webhook.aiohttp_server import SimpleRequestHandler
            from aiohttp import web

            webhook_path = '/webhook/telegram/'
            webhook_secret = settings.TELEGRAM_WEBHOOK_SECRET

            async def health_handler(request):
                return web.Response(text='ok')

            app = web.Application()
            app.router.add_get('/health/', health_handler)
            handler = SimpleRequestHandler(
                dispatcher=dp,
                bot=bot,
                secret_token=webhook_secret,
            )
            handler.register(app, path=webhook_path)

            webhook_url = settings.SITE_URL.rstrip('/') + webhook_path
            await bot.set_webhook(
                url=webhook_url,
                secret_token=webhook_secret,
                drop_pending_updates=True,
            )
            logger.info('Registered webhook: %s', webhook_url)

            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', 8001)  # noqa: S104
            await site.start()
            logger.info('Webhook server listening on :8001')

        tasks.append(shutdown_event.wait())
        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info('Shutting down...')
        await listener.close()
        await bot.session.close()

    asyncio.run(_run())


if __name__ == '__main__':
    poll = '--poll' in sys.argv
    main(poll=poll)
