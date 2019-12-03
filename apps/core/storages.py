from django.conf import settings
from storages.backends.azure_storage import AzureStorage


class PublicAzureStorage(AzureStorage):
    account_name = settings.AZURE_ACCOUNT_NAME
    account_key = settings.AZURE_ACCOUNT_KEY
    azure_container = settings.AZURE_PUBLIC_CONTAINER
    expiration_secs = None
