from ..image import ppoi_position


class TestPpoiPosition:
    # valid PPOI string is converted to CSS object-position
    def test_converts_ppoi_to_css(self):
        assert ppoi_position('0.3x0.7') == '30% 70%'

    # empty string returns the default center position
    def test_empty_returns_default(self):
        assert ppoi_position('') == '50% 50%'

    # None returns the default center position
    def test_none_returns_default(self):
        assert ppoi_position(None) == '50% 50%'

    # malformed string returns the default center position
    def test_invalid_format_returns_default(self):
        assert ppoi_position('invalid') == '50% 50%'

    # boundary values convert correctly
    def test_boundary_values(self):
        assert ppoi_position('0x0') == '0% 0%'
        assert ppoi_position('1x1') == '100% 100%'
