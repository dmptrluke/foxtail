import logging
import time
from pathlib import Path

from huey import crontab
from huey.contrib.djhuey import periodic_task, task
from imagefield.fields import IMAGEFIELDS

from apps.core.storages import LocalReadCache

HEARTBEAT_FILE = Path('/tmp/huey-heartbeat')  # noqa: S108

logger = logging.getLogger(__name__)


@periodic_task(crontab(minute='*'))
def heartbeat():
    """Write a timestamp so the container healthcheck can verify the worker is alive."""
    HEARTBEAT_FILE.write_text(str(time.time()))


@task()
def process_imagefields(app_label, model_name, pk):
    """Generate all renditions for an instance's image fields (runs async via Huey)"""
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
            cache = LocalReadCache(f.storage, skip_exists=True)
            f.storage = cache
            try:
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
            finally:
                f.storage = cache._storage
                cache.cleanup()
            logger.info('Finished processing %s.%s pk=%s field=%s', app_label, model_name, pk, field.name)
