from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.content.models import Page


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


class PageViewTests(TestCase):
    def setUp(self):
        Page.objects.create(title="Page", slug="slug-1", body="TURBO", body_rendered="BEEP")

    def test_template(self):
        response = self.client.get(reverse('page-detail', kwargs={'slug': 'slug-1'}))
        self.assertTemplateUsed(response, 'page.html')

    def test_content(self):
        response = self.client.get(reverse('page-detail', kwargs={'slug': 'slug-1'}))
        self.assertContains(response, "TURBO")
