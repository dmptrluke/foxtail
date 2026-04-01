from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.templatetags.cache import make_template_fragment_key

from .models import Event


@receiver([post_save, post_delete], sender=Event)
def invalidate_event_caches(sender, **kwargs):
    cache.delete(make_template_fragment_key('homepage_events'))
