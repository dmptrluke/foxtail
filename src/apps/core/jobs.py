import logging

from imagefield.fields import IMAGEFIELDS

logger = logging.getLogger(__name__)


def process_imagefields(app_label, model_name, pk):
    from django.apps import apps

    model = apps.get_model(app_label, model_name)
    try:
        instance = model.objects.get(pk=pk)
    except model.DoesNotExist:
        logger.warning('Cannot process images: %s.%s pk=%s not found', app_label, model_name, pk)
        return

    fields = [f for f in IMAGEFIELDS if issubclass(model, f.model)]
    for field in fields:
        f = getattr(instance, field.name)
        if f.name:
            specs = list(f.field.formats)
            logger.info(
                'Processing %d renditions for %s.%s pk=%s field=%s', len(specs), app_label, model_name, pk, field.name
            )
            for spec in specs:
                try:
                    f.process(spec)
                except Exception:
                    logger.exception(
                        'Failed to process rendition %s for %s.%s pk=%s field=%s',
                        spec,
                        app_label,
                        model_name,
                        pk,
                        field.name,
                    )
            logger.info('Finished processing %s.%s pk=%s field=%s', app_label, model_name, pk, field.name)
