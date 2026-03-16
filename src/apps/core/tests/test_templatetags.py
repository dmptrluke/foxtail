from apps.core.templatetags.text import reading_time


class TestReadingTimeFilter:
    """Reading time calculates minutes from word count at 200 wpm."""

    def test_short_text(self):
        # Less than 200 words rounds up to 1 minute minimum
        assert reading_time('<p>Hello world</p>') == '1 min read'

    def test_medium_text(self):
        # 600 words at 200 wpm = 3 minutes
        html = '<p>' + ' '.join(['word'] * 600) + '</p>'
        assert reading_time(html) == '3 min read'

    def test_boundary_rounds_up(self):
        # 500 words at 200 wpm = 2.5 minutes, ceil to 3
        html = '<p>' + ' '.join(['word'] * 500) + '</p>'
        assert reading_time(html) == '3 min read'

    def test_strips_html_tags(self):
        # Only text content counts, not tag names or attributes
        html = '<h1>Title</h1><p><strong>Bold</strong> text with <a href="#">links</a></p>'
        result = reading_time(html)
        assert result == '1 min read'

    def test_empty_string(self):
        # Empty input returns minimum 1 min read
        assert reading_time('') == '1 min read'

    def test_none(self):
        # None input returns minimum 1 min read
        assert reading_time(None) == '1 min read'
