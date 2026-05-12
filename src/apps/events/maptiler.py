import logging
from decimal import Decimal
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)

GEOCODE_URL = 'https://api.maptiler.com/geocoding/{query}.json'


def normalize_address(address):
    """Collapse user-entered address whitespace for geocoding."""
    return ' '.join(address.split())


def geocode(address, api_key):
    """Geocode an address via MapTiler, restricted to NZ/AU. Returns (lat, lon) Decimals or None"""
    query = normalize_address(address)
    if not query:
        return None

    try:
        response = requests.get(
            GEOCODE_URL.format(query=quote(query, safe='')),
            params={'key': api_key, 'country': 'nz,au', 'limit': 1},
            timeout=10,
        )
        response.raise_for_status()
        features = response.json().get('features', [])
        if not features:
            return None
        coords = features[0]['geometry']['coordinates']
        return Decimal(str(coords[1])), Decimal(str(coords[0]))  # GeoJSON is [lon, lat], Django fields are (lat, lon)
    except requests.RequestException:
        logger.warning('MapTiler geocoding failed for address: %s', query, exc_info=True)
        raise
