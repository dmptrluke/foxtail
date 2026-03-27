"""
Async image rendition processing via huey.

Replaces django-imagefield's synchronous post_save processing (IMAGEFIELD_AUTOGENERATE)
with a huey task that runs on the worker. Tracks image and PPOI field changes to avoid
unnecessary task enqueues on unrelated saves. Oversized uploads are downscaled in pre_save
before they reach storage.

Connected in CoreConfig.ready().
"""

from django.db import transaction

from imagefield.fields import IMAGEFIELDS

from apps.core.imaging import downscale_fieldfile
from apps.core.tasks import process_imagefields

# Map each model to its image fields that have rendition formats defined.
# Built once at import time - IMAGEFIELDS is fully populated after all models are loaded.
fields_by_model = {}
for _field in IMAGEFIELDS:
    if _field.formats:
        fields_by_model.setdefault(_field.model, []).append(_field)


def _has_image(instance):
    """Check if any image field on the instance has a file set."""
    return any(getattr(instance, f.name).name for f in fields_by_model.get(type(instance), ()))


def _image_fields_changed(instance):
    """Compare current image/PPOI values against the post_init snapshot."""
    for field in fields_by_model.get(type(instance), ()):
        file = getattr(instance, field.name)
        current = file.name if file else ''
        original = instance.__dict__.get(f'_orig_{field.name}')
        if original is None or current != original:
            return True
        if field.ppoi_field:
            current_ppoi = getattr(instance, field.ppoi_field, '')
            if current_ppoi != instance.__dict__.get(f'_orig_{field.ppoi_field}'):
                return True
    return False


def on_post_init(sender, instance, **kwargs):
    """Snapshot image and PPOI values for change detection."""
    for field in fields_by_model.get(sender, ()):
        file = getattr(instance, field.name)
        instance.__dict__[f'_orig_{field.name}'] = file.name if file else ''
        if field.ppoi_field:
            instance.__dict__[f'_orig_{field.ppoi_field}'] = getattr(instance, field.ppoi_field, '')


def on_pre_save(sender, instance, **kwargs):
    """Downscale oversized image uploads before they're saved to storage."""
    for field in fields_by_model.get(sender, ()):
        downscale_fieldfile(getattr(instance, field.name))


def on_post_save(sender, instance, **kwargs):
    """Enqueue rendition processing if image fields changed."""
    if kwargs.get('created'):
        if not _has_image(instance):
            return
    elif not _image_fields_changed(instance):
        return

    def _enqueue():
        process_imagefields(
            instance._meta.app_label,
            instance._meta.model_name,
            instance.pk,
        )

    transaction.on_commit(_enqueue)
