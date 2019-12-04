from django.dispatch import receiver
from django_cleanup.signals import cleanup_pre_delete


@receiver(cleanup_pre_delete)
def image_delete(**kwargs):

    image = kwargs['file']
    image.delete_all_created_images()
