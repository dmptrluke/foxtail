from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'apps.core'

    def ready(self):
        # import signal handlers
        # noinspection PyUnresolvedReferences
        import apps.core.signals  # noqa: F401
