import pytest
from django.test import TestCase
from django.urls import reverse, resolve

import atoma

from .models import Post


class ResponseCodeTests:
    def test_blog(self, client):
        url = reverse('blog_list')
        response = client.get(url)
        assert response.status_code == 200

    def test_feed(self, client):
        url = reverse('blog_feed')
        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_blog_detail(self, client):
        Post.objects.create(title='1-title', slug='1-slug', text='1-text', author='1-author')
        url = reverse('blog_detail', kwargs={'slug': '1-slug'})
        response = client.get(url)
        assert response.status_code == 200


class URLResolverTests:
    def test_blog(self):
        resolver = resolve('/blog/')
        assert resolver.view_name == 'blog_list'

    def test_feed(self):
        resolver = resolve('/blog/feed/')
        assert resolver.view_name == 'blog_feed'

    def test_blog_detail(self):
        resolver = resolve('/blog/test-post/')
        assert resolver.view_name == 'blog_detail'


class PostModelTest(TestCase):
    def test_string_representation(self):
        post = Post(title="title-1")
        self.assertEqual(str(post), post.title)

    def test_absolute_url(self):
        post = Post(title="title-1", slug="slug-1")
        correct_url = reverse('blog_detail', kwargs={'slug': 'slug-1'})
        self.assertEqual(post.get_absolute_url(), correct_url)


class IndexViewTests(TestCase):
    """Test whether our blog entries show up on the index"""

    def test_template(self):
        response = self.client.get(reverse('index'))
        self.assertTemplateUsed(response, 'index.html')

    def test_one_entry(self):
        with self.settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}):
            Post.objects.create(title='1-title', slug='1-slug', text='1-text', author='1-author')
            response = self.client.get(reverse('index'))
            self.assertContains(response, '1-title')
            self.assertContains(response, '1-text')

    def test_two_entries(self):
        with self.settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}}):
            Post.objects.create(title='1-title', slug='1-slug', text='1-text', author='1-author')
            Post.objects.create(title='2-title', slug='2-slug', text='2-text', author='2-author')
            response = self.client.get(reverse('index'))
            self.assertContains(response, '1-title')
            self.assertContains(response, '1-text')
            self.assertContains(response, '2-title')


class BlogListViewTests(TestCase):
    """Test whether our blog entries show up on the blog"""

    def test_template(self):
        response = self.client.get(reverse('blog_list'))
        self.assertTemplateUsed(response, 'blog_list.html')

    def test_one_entry(self):
        Post.objects.create(title='1-title', slug='1-slug', text='1-text', author='1-author')
        response = self.client.get(reverse('blog_list'))
        self.assertContains(response, '1-title')
        self.assertContains(response, '1-text')

    def test_two_entries(self):
        Post.objects.create(title='1-title', slug='1-slug', text='1-text', author='1-author')
        Post.objects.create(title='2-title', slug='2-slug', text='2-text', author='2-author')
        response = self.client.get(reverse('blog_list'))
        self.assertContains(response, '1-title')
        self.assertContains(response, '1-text')
        self.assertContains(response, '2-title')


class FeedViewTests(TestCase):
    """Test whether our blog entries show up on the feed"""

    def test_one_entry(self):
        Post.objects.create(title='1-title', slug='1-slug', text='1-text', author='1-author')

        response = self.client.get(reverse('blog_feed'))
        feed = atoma.parse_rss_bytes(response.content)

        assert feed.items[0].title == '1-title'
        assert feed.items[0].description == '1-text'

    def test_two_entries(self):
        Post.objects.create(title='1-title', slug='1-slug', text='1-text', author='1-author')
        Post.objects.create(title='2-title', slug='2-slug', text='2-text', author='2-author')

        response = self.client.get(reverse('blog_feed'))
        feed = atoma.parse_rss_bytes(response.content)

        titles = [item.title for item in feed.items]
        descriptions = [item.description for item in feed.items]

        assert '1-title' in titles
        assert '2-title' in titles

        assert '1-text' in descriptions
        assert '2-text' in descriptions


class BlogDetailViewTests(TestCase):
    def setUp(self):
        self.post = Post.objects.create(title='1-title', slug='1-slug', text='1-text', author='1-author')
        self.post.tags.add("green", "blue")

    def test_template(self):
        response = self.client.get(reverse('blog_detail', kwargs={'slug': '1-slug'}))
        self.assertTemplateUsed(response, 'blog_detail.html')

    def test_content(self):
        response = self.client.get(reverse('blog_detail', kwargs={'slug': '1-slug'}))
        self.assertContains(response, '1-title')
        self.assertContains(response, '1-text')

    def test_tags(self):
        response = self.client.get(reverse('blog_detail', kwargs={'slug': '1-slug'}))
        self.assertContains(response, '?tag=blue">Blue')
        self.assertContains(response, '?tag=green">Green')
