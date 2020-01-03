import pytest

from apps.content.models import Page

pytestmark = pytest.mark.django_db


def test_string_representation(page: Page):
    assert str(page) == page.title


def test_get_absolute_url(page: Page):
    assert page.get_absolute_url() == f"/{page.slug}/"
