import hashlib
import logging
from decimal import Decimal

import requests

logger = logging.getLogger(__name__)

GEOCODE_URL = 'https://api.mapbox.com/search/geocode/v6/forward'
STATIC_MAP_BASE = 'https://api.mapbox.com/styles/v1/mapbox/streets-v12/static'


def geocode(address, token):
    """Geocode an address via Mapbox. Returns (latitude, longitude) or None."""
    try:
        response = requests.get(
            GEOCODE_URL,
            params={'q': address, 'country': 'nz,au', 'limit': 1, 'permanent': 'true', 'access_token': token},
            timeout=10,
        )
        response.raise_for_status()
        features = response.json().get('features', [])
        if not features:
            return None
        coords = features[0]['geometry']['coordinates']
        return Decimal(str(coords[1])), Decimal(str(coords[0]))
    except requests.RequestException:
        logger.warning('Mapbox geocoding failed for address: %s', address, exc_info=True)
        return None


def static_map(latitude, longitude, token, *, zoom=15, pin=True, pin_color='e74c3c'):
    """Fetch a static map image from Mapbox. Returns PNG bytes or None."""
    try:
        parts = [STATIC_MAP_BASE]
        if pin:
            parts.append(f'pin-l+{pin_color}({longitude},{latitude})')
        parts.append(f'{longitude},{latitude},{zoom},0')
        parts.append('320x180@2x')
        response = requests.get('/'.join(parts), params={'access_token': token}, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.RequestException:
        logger.warning('Mapbox static map failed for %s,%s', latitude, longitude, exc_info=True)
        return None


def map_filename(address):
    digest = hashlib.md5(address.encode(), usedforsecurity=False).hexdigest()[:12]
    return f'map-{digest}.png'
