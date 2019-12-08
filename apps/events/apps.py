from django.apps import AppConfig


class EventsConfig(AppConfig):
    name = 'apps.events'
    verbose_name = 'Events'

    def ready(self):
        # import signal handlers
        # noinspection PyUnresolvedReferences
        import apps.events.signals  # noqa: F401
