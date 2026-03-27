import logging
from io import BytesIO

from django.conf import settings

import pyvips

logger = logging.getLogger(__name__)

# map vips loader names to output suffixes
_FORMAT_SUFFIX = {
    'jpegload_buffer': '.jpg',
    'pngload_buffer': '.png',
    'webpload_buffer': '.webp',
}


def downscale_image(data, max_dimension=None):
    """Downscale image bytes if either axis exceeds max_dimension.

    Returns new image bytes in the same format, or None if no resize was needed.
    Uses thumbnail_buffer for memory-efficient shrink-on-load (JPEG decodes at 1/8 scale).
    """
    if max_dimension is None:
        max_dimension = settings.MAX_IMAGE_DIMENSION

    # header-only read to check dimensions (vips is lazy, no pixel decode here)
    image = pyvips.Image.new_from_buffer(data, '')

    if max(image.width, image.height) <= max_dimension:
        return None

    loader = image.get('vips-loader')
    suffix = _FORMAT_SUFFIX.get(loader)
    if suffix is None:
        return None

    # thumbnail_buffer does shrink-on-load, keeping peak memory low.
    # width=max_dimension, height defaults to same value, so it fits in a square bounding box.
    resized = pyvips.Image.thumbnail_buffer(data, max_dimension)

    save_kwargs = {}
    if suffix == '.jpg':
        save_kwargs = {'Q': 95, 'interlace': True}
    elif suffix == '.webp':
        save_kwargs = {'Q': 95}

    result = resized.write_to_buffer(suffix, **save_kwargs)

    logger.info(
        'Downscaled %dx%d (%d bytes) to %dx%d (%d bytes)',
        image.width,
        image.height,
        len(data),
        resized.width,
        resized.height,
        len(result),
    )

    return result


def downscale_fieldfile(fieldfile, max_dimension=None):
    """Downscale an uncommitted FieldFile upload in-place. Returns True if modified."""
    if not fieldfile or not fieldfile.name or fieldfile._committed:
        return False

    upload = fieldfile.file
    if upload is None:
        return False

    data = upload.read()
    upload.seek(0)

    try:
        result = downscale_image(data, max_dimension)
    except pyvips.Error:
        logger.warning('Failed to load image for downscaling: %s', fieldfile.name, exc_info=True)
        return False

    if result is None:
        return False

    fieldfile.file = BytesIO(result)
    return True
