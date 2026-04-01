from django import template
from django.core.cache import cache
from django.db.models import Count

from published.utils import queryset_filter

from apps.blog.models import Post

register = template.Library()

CACHE_KEY = 'blog_sidebar_data'
_CACHE_TTL = 3600


@register.inclusion_tag('blog/_sidebar.html', takes_context=True)
def blog_sidebar(context):
    """Render the blog sidebar with cached post and tag data."""
    data = cache.get(CACHE_KEY)
    if data is None:
        data = {
            'sidebar_post_list': list(
                queryset_filter(Post.objects)
                .only('title', 'slug', 'created', 'text_rendered', 'publish_status', 'live_as_of')
                .all()[:3]
            ),
            'sidebar_tag_list': list(
                Post.tags.annotate(num_times=Count('taggit_taggeditem_items')).order_by('-num_times')[:8]
            ),
        }
        cache.set(CACHE_KEY, data, _CACHE_TTL)
    data['request'] = context.get('request')
    return data
