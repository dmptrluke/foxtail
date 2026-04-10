from django.apps import AppConfig


class BlogConfig(AppConfig):
    name = 'apps.blog'
    label = 'blog'
    verbose_name = 'Blog'

    def ready(self):
        from . import signals  # noqa: F401
