from django.test import TestCase
from django.urls import reverse

from apps.content.models import Page


class PageModelTest(TestCase):
    def test_string_representation(self):
        page = Page(title="My entry title")
        self.assertEqual(str(page), page.title)

    def test_absolute_url(self):
        page = Page(title="title-1", slug="slug-1")
        correct_url = reverse('page-detail', kwargs={'slug': 'slug-1'})
        self.assertEqual(page.get_absolute_url(), correct_url)
