from django.test import TestCase
from django.urls import reverse, resolve

import atoma

from .models import Post


class ResponseCodeTests(TestCase):
    def test_blog(self):
        url = reverse('blog_list')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_feed(self):
        url = reverse('blog_feed')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_blog_detail(self):
        Post.objects.create(title='1-title', slug='1-slug', text='1-text', author='1-author')
        url = reverse('blog_detail', kwargs={'slug': '1-slug'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)


class URLResolverTests(TestCase):
    def test_blog(self):
        resolver = resolve('/blog/')
        self.assertEquals(resolver.view_name, 'blog_list')

    def test_feed(self):
        resolver = resolve('/blog/feed/')
        self.assertEquals(resolver.view_name, 'blog_feed')

    def test_blog_detail(self):
        resolver = resolve('/blog/test-post/')
        self.assertEquals(resolver.view_name, 'blog_detail')


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

        assert feed.items[0].title == '1-title'
        assert feed.items[0].description == '1-text'

        assert feed.items[1].title == '2-title'
        assert feed.items[1].description == '2-text'


class BlogDetailViewTests(TestCase):
    def setUp(self):
        Post.objects.create(title='1-title', slug='1-slug', text='1-text', author='1-author')

    def test_template(self):
        response = self.client.get(reverse('blog_detail', kwargs={'slug': '1-slug'}))
        self.assertTemplateUsed(response, 'blog_detail.html')

    def test_content(self):
        response = self.client.get(reverse('blog_detail', kwargs={'slug': '1-slug'}))
        self.assertContains(response, '1-title')
        self.assertContains(response, '1-text')

