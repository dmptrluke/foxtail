from unittest.mock import MagicMock, PropertyMock

from ..avatar import _default_avatar, avatar_url


class TestAvatarUrl:
    # size <= 80 selects the small rendition
    def test_selects_small_rendition(self):
        user = MagicMock()
        user.avatar = MagicMock()
        user.avatar.small = '/media/avatars/small.jpg'
        assert avatar_url(user, size=40) == '/media/avatars/small.jpg'

    # size <= 160 selects the medium rendition
    def test_selects_medium_rendition(self):
        user = MagicMock()
        user.avatar = MagicMock()
        user.avatar.medium = '/media/avatars/medium.jpg'
        assert avatar_url(user, size=120) == '/media/avatars/medium.jpg'

    # size <= 400 selects the large rendition
    def test_selects_large_rendition(self):
        user = MagicMock()
        user.avatar = MagicMock()
        user.avatar.large = '/media/avatars/large.jpg'
        assert avatar_url(user, size=300) == '/media/avatars/large.jpg'

    # size > 400 falls back to the large rendition
    def test_over_400_uses_large(self):
        user = MagicMock()
        user.avatar = MagicMock()
        user.avatar.large = '/media/avatars/large.jpg'
        assert avatar_url(user, size=500) == '/media/avatars/large.jpg'

    # exception during rendition lookup returns a default SVG avatar
    def test_fallback_on_exception(self):
        user = MagicMock()
        user.avatar = MagicMock()
        user.avatar.small = PropertyMock(side_effect=Exception('broken'))
        type(user.avatar).small = PropertyMock(side_effect=Exception('broken'))
        user.pk = 1
        user.get_short_name.return_value = 'A'
        result = avatar_url(user, size=40)
        assert result.startswith('data:image/svg+xml,')

    # user without avatar gets a default SVG avatar
    def test_no_avatar(self):
        user = MagicMock()
        user.avatar = None
        user.pk = 5
        user.get_short_name.return_value = 'B'
        result = avatar_url(user, size=40)
        assert result.startswith('data:image/svg+xml,')


class TestDefaultAvatar:
    # SVG contains the user's first initial
    def test_contains_initial(self):
        user = MagicMock(pk=1)
        user.get_short_name.return_value = 'Alice'
        result = _default_avatar(user, 40)
        assert '>A</text>' in result

    # same pk always produces the same hue
    def test_deterministic_color(self):
        user = MagicMock(pk=42)
        user.get_short_name.return_value = 'X'
        result1 = _default_avatar(user, 40)
        result2 = _default_avatar(user, 40)
        assert result1 == result2
        hue = (42 * 137) % 360
        assert f'hsl({hue},40%,60%)' in result1

    # HTML-special characters in the name are escaped
    def test_escapes_special_characters(self):
        user = MagicMock(pk=1)
        user.get_short_name.return_value = '<script>'
        result = _default_avatar(user, 40)
        assert '&lt;' in result
        assert '<script>' not in result
