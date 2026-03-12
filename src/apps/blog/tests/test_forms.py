import pytest

from ..forms import PostForm
from ..models import Post

pytestmark = pytest.mark.django_db


class TestPostForm:
    # user with blog_author gets it set as initial author
    def test_author_prepopulated(self, user, author):
        author.user = user
        author.save()
        form = PostForm(user=user)
        assert form.fields['author'].initial == author

    # existing post's tags loaded into initial field
    def test_tags_loaded_on_edit(self, post: Post):
        post.tags.add('news', 'update')
        form = PostForm(instance=post)
        assert set(form.fields['tags'].initial) == set(post.tags.all())
