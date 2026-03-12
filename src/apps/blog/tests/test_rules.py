import pytest

from ..models import Comment, Post
from ..rules import is_author

pytestmark = pytest.mark.django_db


class TestIsAuthor:
    # Post author matches when author.user is the current user
    def test_post_author_matches(self, user, post: Post):
        post.author.user = user
        post.author.save()
        assert is_author(user, post)

    # Comment author matches when comment.author is the current user
    def test_comment_author_matches(self, user, post: Post):
        comment = Comment.objects.create(post=post, author=user, text='test')
        assert is_author(user, comment)

    # returns False for a different user
    def test_different_user(self, user, second_user, post: Post):
        post.author.user = user
        post.author.save()
        assert not is_author(second_user, post)

    # returns False when obj is None
    def test_no_object(self, user):
        assert not is_author(user, None)

    # returns False when author field is None
    def test_no_author(self, user, post: Post):
        post.author = None
        post.save()
        assert not is_author(user, post)
