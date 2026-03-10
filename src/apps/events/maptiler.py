import logging
from decimal import Decimal

import requests

logger = logging.getLogger(__name__)

GEOCODE_URL = 'https://api.maptiler.com/geocoding/{query}.json'


def geocode(address, api_key):
    try:
        response = requests.get(
            GEOCODE_URL.format(query=address),
            params={'key': api_key, 'country': 'nz,au', 'limit': 1},
            timeout=10,
        )
        response.raise_for_status()
        features = response.json().get('features', [])
        if not features:
            return None
        coords = features[0]['geometry']['coordinates']
        return Decimal(str(coords[1])), Decimal(str(coords[0]))
    except requests.RequestException:
        logger.warning('MapTiler geocoding failed for address: %s', address, exc_info=True)
        return None
