from django.db.models.signals import post_save
from django.dispatch import receiver

from versatileimagefield.image_warmer import VersatileImageFieldWarmer

from .models import Post


@receiver(post_save, sender=Post)
def warm_post_images(sender, instance, **kwargs):
    if instance.image:
        warmer = VersatileImageFieldWarmer(
            instance_or_queryset=instance,
            rendition_key_set='post_image',
            image_attr='image'
        )
        warmer.warm()
