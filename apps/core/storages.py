from django.conf import settings
from storages.backends.azure_storage import AzureStorage


class StaticAzureStorage(AzureStorage):
    azure_container = settings.AZURE_STATIC_CONTAINER


class MediaAzureStorage(AzureStorage):
    azure_container = settings.AZURE_MEDIA_CONTAINER
