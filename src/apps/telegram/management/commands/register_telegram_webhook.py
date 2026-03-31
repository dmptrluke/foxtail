from django.conf import settings
from django.core.management.base import BaseCommand

from apps.telegram import api


class Command(BaseCommand):
    help = 'Register or remove the Telegram bot webhook URL and commands'

    def add_arguments(self, parser):
        parser.add_argument('--delete', action='store_true', help='Remove webhook instead of registering')

    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stderr.write('TELEGRAM_BOT_TOKEN is not set')
            return

        if options['delete']:
            api.delete_webhook(drop_pending_updates=True)
            self.stdout.write('Webhook deleted')
            return

        url = settings.SITE_URL.rstrip('/') + '/telegram/webhook/'
        secret = settings.TELEGRAM_WEBHOOK_SECRET
        api.set_webhook(url, secret_token=secret, drop_pending_updates=True)
        api.set_my_commands(
            [
                {'command': 'link', 'description': 'Link your Telegram account to furry.nz'},
                {'command': 'status', 'description': 'Check your link status'},
                {'command': 'unlink', 'description': 'Remove your account link'},
                {'command': 'ping', 'description': 'Check if the bot is running'},
                {'command': 'help', 'description': 'Show available commands'},
            ]
        )
        self.stdout.write(f'Webhook registered: {url}')
