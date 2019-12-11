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


class PageViewTests(TestCase):
    def setUp(self):
        Page.objects.create(title="Page", slug="slug-1", body="TURBO", body_rendered="BEEP")

    def test_template(self):
        response = self.client.get(reverse('page-detail', kwargs={'slug': 'slug-1'}))
        self.assertTemplateUsed(response, 'page.html')

    def test_content(self):
        response = self.client.get(reverse('page-detail', kwargs={'slug': 'slug-1'}))
        self.assertContains(response, "TURBO")
