from storages.backends.azure_storage import AzureStorage


# noinspection PyAbstractClass
class StaticAzureStorage(AzureStorage):
    azure_container = 'static'
    cache_control = 'public,max-age=31536000,immutable'


# noinspection PyAbstractClass
class MediaAzureStorage(AzureStorage):
    azure_container = 'media'
    cache_control = 'public,max-age=604800,immutable'
