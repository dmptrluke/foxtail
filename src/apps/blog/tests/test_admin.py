from django.urls import reverse
from django.utils.html import format_html

import pytest

from ..admin import CommentAdmin, PostAdmin
from ..models import Comment

pytestmark = pytest.mark.django_db


class TestPostAdmin:
    # formats tags as sorted comma-separated string
    def test_tag_list(self, post):
        result = PostAdmin.tag_list(post)
        tag_names = sorted(t.name for t in post.tags.all())
        assert result == ', '.join(tag_names)


class TestCommentAdmin:
    # returns HTML link to the parent post's admin change page
    def test_post_link(self, post, user):
        comment = Comment.objects.create(post=post, author=user, text='test')
        admin = CommentAdmin(Comment, None)
        expected = format_html(
            '<a href="{}">{}</a>',
            reverse('admin:blog_post_change', args=(post.pk,)),
            post.title,
        )
        assert admin.post_link(comment) == expected

    # truncates comment text to 50 characters
    def test_text_preview(self, post, user):
        long_text = 'a' * 100
        comment = Comment.objects.create(post=post, author=user, text=long_text)
        admin = CommentAdmin(Comment, None)
        result = admin.text_preview(comment)
        assert len(result) <= 53
        assert result.endswith('…')
