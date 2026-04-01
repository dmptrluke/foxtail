from django.apps import AppConfig


class EventsConfig(AppConfig):
    name = 'apps.events'
    verbose_name = 'Events'

    def ready(self):
        from . import rules, signals  # noqa: F401
