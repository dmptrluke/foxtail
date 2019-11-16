from django.db.models.signals import post_save
from django.dispatch import receiver
from versatileimagefield.image_warmer import VersatileImageFieldWarmer

from .models import Post


@receiver(post_save, sender=Post)
def warm_post_thumbnail_images(sender, instance, **kwargs):
    if instance.image:
        warmer = VersatileImageFieldWarmer(
            instance_or_queryset=instance,
            rendition_key_set=[
                ('banner', 'crop__800x350'),
                ('thumb', 'crop__300x150')
            ],
            image_attr='image'
        )
        warmer.warm()
