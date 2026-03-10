from decimal import Decimal
from unittest.mock import Mock, patch

import requests

from ..maptiler import geocode


class TestGeocode:
    """Test MapTiler geocoding wrapper."""

    @patch('apps.events.maptiler.requests.get')
    def test_returns_coords_on_success(self, mock_get):
        # geocode returns (lat, lng) from MapTiler GeoJSON response
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                'features': [
                    {
                        'geometry': {
                            'coordinates': [174.776236, -41.28646],
                        }
                    }
                ]
            },
        )
        result = geocode('TSB Arena, Wellington', 'test-key')
        assert result == (Decimal('-41.28646'), Decimal('174.776236'))

    @patch('apps.events.maptiler.requests.get')
    def test_returns_none_on_empty_results(self, mock_get):
        # geocode returns None when no features match
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {'features': []},
        )
        assert geocode('nonexistent place', 'test-key') is None

    @patch('apps.events.maptiler.requests.get')
    def test_returns_none_on_network_error(self, mock_get):
        # geocode returns None on network failure
        mock_get.side_effect = requests.RequestException('timeout')
        assert geocode('TSB Arena', 'test-key') is None
