import logging

from huey.contrib.djhuey import task

logger = logging.getLogger(__name__)


@task(retries=2, retry_delay=5)
def geocode_event(pk, address):
    """Async geocode an event's address and update its coordinates"""
    from django.conf import settings

    from .maptiler import geocode
    from .models import Event

    api_key = getattr(settings, 'MAPTILER_API_KEY', None)
    if not api_key:
        return

    try:
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        logger.warning('Cannot geocode: Event pk=%s not found', pk)
        return

    try:
        coords = geocode(address, api_key)
    except Exception:
        # Re-raise so Huey retries (retries=2); log captures the attempt
        logger.warning('Geocoding error for Event pk=%s address: %s', pk, address, exc_info=True)
        raise

    if coords:
        event.latitude, event.longitude = coords
        event.save(update_fields=['latitude', 'longitude'])
        logger.info('Geocoded Event pk=%s: %s, %s', pk, coords[0], coords[1])
    else:
        logger.warning('Geocoding failed for Event pk=%s address: %s', pk, address)
