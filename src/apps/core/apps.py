from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'apps.core'

    def ready(self):
        from django.db.models import signals

        from apps.core.signals import fields_by_model, on_post_init, on_post_save

        # Wire up async image processing for all models with imagefield formats.
        # post_init snapshots original values; post_save enqueues processing if changed.
        for model in fields_by_model:
            signals.post_init.connect(on_post_init, sender=model, weak=False)
            signals.post_save.connect(on_post_save, sender=model, weak=False)
