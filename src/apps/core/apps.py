from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'apps.core'

    def ready(self):
        from django.db.models import signals

        from apps.core.signals import fields_by_model, on_post_init, on_post_save, on_pre_save

        # Wire up image processing signals for all models with imagefield formats.
        # pre_save downscales oversized uploads; post_init snapshots values for change
        # detection; post_save enqueues async rendition processing if changed.
        for model in fields_by_model:
            signals.pre_save.connect(on_pre_save, sender=model, weak=False)
            signals.post_init.connect(on_post_init, sender=model, weak=False)
            signals.post_save.connect(on_post_save, sender=model, weak=False)
