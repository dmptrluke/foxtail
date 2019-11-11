from django.test import TestCase
from django.urls import reverse, resolve

from .models import Post


class ResponseCodeTests(TestCase):
    def test_blog(self):
        url = reverse('blog')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_blog_detail(self):
        Post.objects.create(title='1-title', slug='1-slug', text='1-text', author='1-author')
        url = reverse('blog-detail', kwargs={'slug': '1-slug'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)


class URLResolverTests(TestCase):
    def test_blog(self):
        resolver = resolve('/blog/')
        self.assertEquals(resolver.view_name, 'blog')

    def test_blog_detail(self):
        resolver = resolve('/blog/test-post/')
        self.assertEquals(resolver.view_name, 'blog-detail')


class PostModelTest(TestCase):
    def test_string_representation(self):
        post = Post(title="title-1")
        self.assertEqual(str(post), post.title)

    def test_absolute_url(self):
        post = Post(title="title-1", slug="slug-1")
        correct_url = reverse('blog-detail', kwargs={'slug': 'slug-1'})
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
        response = self.client.get(reverse('blog'))
        self.assertTemplateUsed(response, 'blog_list.html')

    def test_one_entry(self):
        Post.objects.create(title='1-title', slug='1-slug', text='1-text', author='1-author')
        response = self.client.get(reverse('blog'))
        self.assertContains(response, '1-title')
        self.assertContains(response, '1-text')

    def test_two_entries(self):
        Post.objects.create(title='1-title', slug='1-slug', text='1-text', author='1-author')
        Post.objects.create(title='2-title', slug='2-slug', text='2-text', author='2-author')
        response = self.client.get(reverse('blog'))
        self.assertContains(response, '1-title')
        self.assertContains(response, '1-text')
        self.assertContains(response, '2-title')


class BlogDetailViewTests(TestCase):
    def setUp(self):
        Post.objects.create(title='1-title', slug='1-slug', text='1-text', author='1-author')

    def test_template(self):
        response = self.client.get(reverse('blog-detail', kwargs={'slug': '1-slug'}))
        self.assertTemplateUsed(response, 'blog_detail.html')

    def test_content(self):
        response = self.client.get(reverse('blog-detail', kwargs={'slug': '1-slug'}))
        self.assertContains(response, '1-title')
        self.assertContains(response, '1-text')
