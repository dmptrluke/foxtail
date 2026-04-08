from django.contrib.sitemaps import Sitemap

from .models import EventSeries, Organisation


class OrganisationSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return Organisation.objects.all()

    def lastmod(self, obj):
        return obj.modified


class EventSeriesSitemap(Sitemap):
    priority = 0.4
    changefreq = 'weekly'

    def items(self):
        return EventSeries.objects.all()

    def lastmod(self, obj):
        return obj.modified
