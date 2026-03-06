from decimal import Decimal
from unittest.mock import Mock, patch

import requests

from ..mapbox import geocode, static_map


class TestGeocode:
    """Test Mapbox geocoding wrapper."""

    @patch('apps.events.mapbox.requests.get')
    def test_returns_coords_on_success(self, mock_get):
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
        result = geocode('TSB Arena, Wellington', 'test-token')
        assert result == (Decimal('-41.28646'), Decimal('174.776236'))

    @patch('apps.events.mapbox.requests.get')
    def test_returns_none_on_empty_results(self, mock_get):
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {'features': []},
        )
        assert geocode('nonexistent place', 'test-token') is None

    @patch('apps.events.mapbox.requests.get')
    def test_returns_none_on_network_error(self, mock_get):
        mock_get.side_effect = requests.RequestException('timeout')
        assert geocode('TSB Arena', 'test-token') is None


class TestStaticMap:
    """Test Mapbox static map image wrapper."""

    @patch('apps.events.mapbox.requests.get')
    def test_returns_bytes_on_success(self, mock_get):
        mock_get.return_value = Mock(status_code=200, content=b'\x89PNG')
        result = static_map(Decimal('-41.28646'), Decimal('174.776236'), 'test-token')
        assert result == b'\x89PNG'

    @patch('apps.events.mapbox.requests.get')
    def test_returns_none_on_network_error(self, mock_get):
        mock_get.side_effect = requests.RequestException('timeout')
        assert static_map(Decimal('-41.28646'), Decimal('174.776236'), 'test-token') is None
