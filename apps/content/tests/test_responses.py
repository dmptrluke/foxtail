from django.test import TestCase
from django.urls import reverse, resolve


class ResponseCodeTests(TestCase):
    def test_index(self):
        url = reverse('index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class URLResolverTests(TestCase):
    def test_index(self):
        resolver = resolve('/')
        self.assertEqual(resolver.view_name, 'index')

    def test_page(self):
        resolver = resolve('/frequently-asked-questions/')
        self.assertEqual(resolver.view_name, 'page-detail')
