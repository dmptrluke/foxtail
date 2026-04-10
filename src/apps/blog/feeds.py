import html
import logging

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.feedgenerator import Atom1Feed, Enclosure
from django.utils.html import strip_tags
from django.utils.text import Truncator

from published.utils import queryset_filter

from apps.core.models import SiteSettings

from .models import Post

logger = logging.getLogger(__name__)


class FoxtailAtomFeed(Atom1Feed):
    """Atom feed with full HTML content and webfeeds namespace."""

    def root_attributes(self):
        attrs = super().root_attributes()
        attrs['xmlns:webfeeds'] = 'http://webfeeds.org/rss/1.0'
        return attrs

    def add_root_elements(self, handler):
        super().add_root_elements(handler)
        if self.feed.get('webfeeds_icon'):
            handler.addQuickElement('webfeeds:icon', self.feed['webfeeds_icon'])
        if self.feed.get('webfeeds_logo'):
            handler.addQuickElement('webfeeds:logo', self.feed['webfeeds_logo'])
        if self.feed.get('webfeeds_accent_color'):
            handler.addQuickElement('webfeeds:accentColor', self.feed['webfeeds_accent_color'])
        handler.addQuickElement('webfeeds:related', '', {'layout': 'card', 'target': 'browser'})

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        if item.get('content_html'):
            handler.addQuickElement('content', item['content_html'], {'type': 'html'})


class LatestEntriesFeed(Feed):
    feed_type = FoxtailAtomFeed
    title = 'Latest News'
    link = reverse_lazy('blog:list')
    subtitle = 'The latest furry news.'

    def feed_url(self):
        return reverse_lazy('blog:feed')

    def feed_extra_kwargs(self, obj):
        conf = SiteSettings.get_solo()
        return {
            'webfeeds_icon': self._absolute_static('images/paw-96.png'),
            'webfeeds_logo': self._absolute_static('images/paw.svg'),
            'webfeeds_accent_color': conf.theme_color.lstrip('#'),
        }

    def items(self):
        return queryset_filter(Post.objects).select_related('author').prefetch_related('tags').order_by('-created')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        """Short summary for the Atom <summary> element."""
        if item.description:
            return item.description
        return Truncator(html.unescape(strip_tags(item.text_rendered))).chars(200)

    def item_pubdate(self, item):
        return item.created

    def item_updateddate(self, item):
        return item.modified

    def item_author_name(self, item):
        if item.author:
            return item.author.name
        return None

    def item_categories(self, item):
        return [tag.name for tag in item.tags.all()]

    def item_enclosures(self, item):
        if not item.image:
            return []
        try:
            url = item.image.card_2x
            if not url.startswith('http'):
                url = settings.SITE_URL + url
            return [self._enclosure(url)]
        except Exception:
            logger.exception('Missing image rendition for post %s', item.pk)
            return []

    @staticmethod
    def _absolute_static(path):
        url = static(path)
        if not url.startswith('http'):
            url = settings.SITE_URL + url
        return url

    @staticmethod
    def _enclosure(url):
        return Enclosure(url=url, length='0', mime_type='image/webp')

    def item_extra_kwargs(self, item):
        return {'content_html': item.text_rendered}


__all__ = ['LatestEntriesFeed']
