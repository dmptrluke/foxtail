from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.templatetags.cache import make_template_fragment_key

from .models import Post


@receiver([post_save, post_delete], sender=Post)
def invalidate_post_caches(sender, instance, **kwargs):
    from .templatetags.blog_sidebar import CACHE_KEY as SIDEBAR_CACHE_KEY

    cache.delete(SIDEBAR_CACHE_KEY)
    cache.delete(make_template_fragment_key('homepage_news'))
