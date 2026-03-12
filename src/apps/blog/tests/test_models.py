from unittest.mock import PropertyMock, patch

import pytest

from ..models import Author, Comment, Post

pytestmark = pytest.mark.django_db


class TestPost:
    # __str__ returns the title
    def test_string_representation(self, post: Post):
        assert str(post) == post.title

    # URL follows /blog/<slug>/ pattern
    def test_get_absolute_url(self, post: Post):
        assert post.get_absolute_url() == f'/blog/{post.slug}/'


class TestPostStructuredData:
    # base fields: type, headline, url, publisher, dates
    def test_required_fields(self, post: Post):
        sd = post.structured_data
        assert sd['@type'] == 'BlogPosting'
        assert sd['headline'] == post.title
        assert sd['url'].endswith(f'/blog/{post.slug}/')
        assert sd['publisher'] == {'@id': 'https://furry.nz/#organization'}
        assert sd['datePublished'] == post.created
        assert sd['dateModified'] == post.modified

    # author name included when post has an author
    def test_with_author(self, post: Post):
        sd = post.structured_data
        assert sd['author'] == {'@type': 'Person', 'name': post.author.name}

    # author is None when post has no author
    def test_without_author(self, post: Post):
        post.author = None
        post.save()
        post.__dict__.pop('structured_data', None)
        sd = post.structured_data
        assert sd['author'] is None

    # falls back to truncated rendered text when description is empty
    def test_description_fallback(self, post: Post):
        post.description = ''
        post.save()
        post.__dict__.pop('structured_data', None)
        sd = post.structured_data
        assert len(sd['description']) > 0

    # tags appear as keywords list
    def test_keywords_from_tags(self, post: Post):
        sd = post.structured_data
        assert sd['keywords'] == [tag.name for tag in post.tags.all()]

    # relative image URL gets SITE_URL prepended
    def test_image_relative_url(self, post: Post):
        with patch.object(type(post), 'image', new_callable=PropertyMock) as mock_image:
            mock_obj = mock_image.return_value

            mock_obj.card_2x = '/media/blog/test.jpg'
            post.__dict__.pop('structured_data', None)
            sd = post.structured_data
            assert sd['image']['@type'] == 'ImageObject'
            assert sd['image']['url'] == 'http://localhost:8000/media/blog/test.jpg'
            assert sd['image']['width'] == 1200
            assert sd['image']['height'] == 630

    # absolute image URL used as-is
    def test_image_absolute_url(self, post: Post):
        with patch.object(type(post), 'image', new_callable=PropertyMock) as mock_image:
            mock_obj = mock_image.return_value

            mock_obj.card_2x = 'https://cdn.example.com/blog/test.jpg'
            post.__dict__.pop('structured_data', None)
            sd = post.structured_data
            assert sd['image']['url'] == 'https://cdn.example.com/blog/test.jpg'

    # no image block when post has no image
    def test_without_image(self, post: Post):
        sd = post.structured_data
        assert 'image' not in sd


class TestAuthor:
    # __str__ returns the name
    def test_string_representation(self, author: Author):
        assert str(author) == author.name


class TestComment:
    # __str__ returns the comment text
    def test_string_representation(self, comment: Comment):
        assert str(comment) == comment.text
