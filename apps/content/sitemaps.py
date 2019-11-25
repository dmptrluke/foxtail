from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Page


class StaticSitemap(Sitemap):
    priority = 0.6
    changefreq = 'daily'

    def items(self):
        return ['index', 'blog_list']

    def location(self, item):
        return reverse(item)


class PageSitemap(Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return Page.objects.filter(show_in_menu=True)
