from django.dispatch import receiver

from django_cleanup.signals import cleanup_pre_delete
from versatileimagefield.files import VersatileImageFieldFile


@receiver(cleanup_pre_delete)
def image_delete(**kwargs):

    image = kwargs['file']

    if isinstance(image, VersatileImageFieldFile):
        image.delete_all_created_images()
