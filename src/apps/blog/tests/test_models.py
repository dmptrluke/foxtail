import pytest

from ..models import Post

pytestmark = pytest.mark.django_db


class TestPost:
    def test_string_representation(self, post: Post):
        assert str(post) == post.title

    def test_get_absolute_url(self, post: Post):
        assert post.get_absolute_url() == f"/blog/{post.slug}/"
