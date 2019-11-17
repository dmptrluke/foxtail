from django.contrib.auth import get_user_model
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


class IndexViewTests(TestCase):
    def test_template(self):
        response = self.client.get(reverse('index'))
        self.assertTemplateUsed(response, 'index.html')

    def test_content(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, "To continue, you'll need to create a")


class AuthenticatedIndexViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('user1', 'user1@example.com')
        self.client.force_login(self.user)

    def test_content(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, "You're now logged in as <strong>user1")
