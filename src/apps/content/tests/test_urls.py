from django.urls import resolve, reverse


class TestContentUrls:
    """Test content URL routing."""

    # index resolves to root
    def test_index(self):
        assert reverse('content:index') == '/'
        assert resolve('/').view_name == 'content:index'

    # page resolves with slug
    def test_page(self):
        assert reverse('content:page', kwargs={'slug': 'about'}) == '/about/'
        assert resolve('/about/').view_name == 'content:page'
