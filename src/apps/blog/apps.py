from django.apps import AppConfig


class BlogConfig(AppConfig):
    name = 'apps.blog'
    label = 'foxtail_blog'
    verbose_name = 'Blog'

    def ready(self):
        # import signal handlers
        # noinspection PyUnresolvedReferences
        import apps.blog.signals  # noqa: F401
