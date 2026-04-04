from django.apps import AppConfig


class ImagesConfig(AppConfig):
    name = 'apps.images'

    def ready(self):
        from django.db.models import signals

        from apps.images.signals import fields_by_model, on_post_init, on_post_save, on_pre_save

        for model in fields_by_model:
            signals.pre_save.connect(on_pre_save, sender=model, weak=False)
            signals.post_init.connect(on_post_init, sender=model, weak=False)
            signals.post_save.connect(on_post_save, sender=model, weak=False)
