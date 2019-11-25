from django.contrib.sitemaps import Sitemap

from .models import Event


class EventSitemap(Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return Event.objects.all()

    def lastmod(self, obj):
        return obj.modified
