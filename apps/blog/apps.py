from django.apps import AppConfig


class BlogConfig(AppConfig):
    name = 'apps.blog'

    def ready(self):
        # import signal handlers
        # noinspection PyUnresolvedReferences
        import apps.blog.signals
