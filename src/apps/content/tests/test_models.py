import pytest

from apps.content.models import Page

pytestmark = pytest.mark.django_db


class TestPage:
    """Test Page model."""

    # __str__ returns the title
    def test_str(self, page: Page):
        assert str(page) == page.title

    # get_absolute_url uses the slug
    def test_get_absolute_url(self, page: Page):
        assert page.get_absolute_url() == f'/{page.slug}/'
