from django.contrib.sitemaps import Sitemap

from published.utils import queryset_filter

from .models import Post


class PostSitemap(Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return queryset_filter(Post.objects).all()

    def lastmod(self, obj):
        return obj.modified
