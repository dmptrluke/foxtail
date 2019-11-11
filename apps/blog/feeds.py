from django.contrib.syndication.views import Feed
from markdownx.utils import markdownify
from django.utils.html import strip_tags
from .models import Post


class LatestEntriesFeed(Feed):
    title = "furry.nz news"
    link = "/blog/"
    description = "furry.nz news."

    def items(self):
        return Post.objects.order_by('-created')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return strip_tags(markdownify(item.text))

    def item_pubdate(self, item):
        return item.created
