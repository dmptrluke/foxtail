from django.test import TestCase
from django.urls import reverse, resolve


class ResponseCodeTests(TestCase):
    def test_index(self):
        url = reverse('index')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)


class URLResolverTests(TestCase):
    def test_index(self):
        resolver = resolve('/')
        self.assertEquals(resolver.view_name, 'index')


class IndexViewTests(TestCase):
    def test_template(self):
        response = self.client.get(reverse('index'))
        self.assertTemplateUsed(response, 'index.html')
