import logging
from decimal import Decimal

import requests

logger = logging.getLogger(__name__)

GEOCODE_URL = 'https://api.mapbox.com/search/geocode/v6/forward'
STATIC_MAP_URL = 'https://api.mapbox.com/styles/v1/mapbox/streets-v12/static/{lng},{lat},14,0/640x360@2x'


def geocode(address, token):
    """Geocode an address via Mapbox. Returns (latitude, longitude) or None."""
    try:
        response = requests.get(
            GEOCODE_URL,
            params={'q': address, 'country': 'nz', 'limit': 1, 'access_token': token},
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


def static_map(latitude, longitude, token):
    """Fetch a static map image from Mapbox. Returns PNG bytes or None."""
    try:
        url = STATIC_MAP_URL.format(lat=latitude, lng=longitude)
        response = requests.get(url, params={'access_token': token}, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.RequestException:
        logger.warning('Mapbox static map failed for %s,%s', latitude, longitude, exc_info=True)
        return None
