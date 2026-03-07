from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'apps.core'

    def ready(self):
        from django.db.models import signals

        import django_rq
        from imagefield.fields import IMAGEFIELDS

        from apps.core.jobs import process_imagefields

        def enqueue_image_processing(sender, instance, **kwargs):
            django_rq.enqueue(
                process_imagefields,
                instance._meta.app_label,
                instance._meta.model_name,
                instance.pk,
            )

        connected = set()
        for field in IMAGEFIELDS:
            if field.formats and field.model not in connected:
                connected.add(field.model)
                signals.post_save.connect(enqueue_image_processing, sender=field.model, weak=False)
