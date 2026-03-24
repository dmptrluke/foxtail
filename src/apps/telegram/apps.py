from django.apps import AppConfig


class TelegramConfig(AppConfig):
    name = 'apps.telegram'
    verbose_name = 'Telegram'

    def ready(self):
        from allauth.socialaccount.signals import social_account_added, social_account_removed, social_account_updated

        from . import signals

        social_account_added.connect(signals.on_social_account_changed)
        social_account_updated.connect(signals.on_social_account_changed)
        social_account_removed.connect(signals.on_social_account_removed)
