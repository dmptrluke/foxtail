from django.apps import AppConfig


class DirectoryConfig(AppConfig):
    name = 'apps.directory'

    def ready(self):
        pass
        # import signal handlers
        # noinspection PyUnresolvedReferences
        # import apps.directory.signals  # noqa: F401
