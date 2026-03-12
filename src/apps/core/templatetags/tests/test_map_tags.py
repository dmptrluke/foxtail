from ..map_tags import map_style_url


class TestMapStyleUrl:
    # returns a Maptiler URL with the style name and API key
    def test_returns_url_with_key(self, settings):
        settings.MAPTILER_API_KEY = 'test-key'
        result = map_style_url('streets')
        assert result == 'https://api.maptiler.com/maps/streets/style.json?key=test-key'

    # returns empty string when no API key is configured
    def test_returns_empty_without_key(self, settings):
        settings.MAPTILER_API_KEY = ''
        assert map_style_url('streets') == ''
