from storages.backends.s3 import S3Storage


# noinspection PyAbstractClass
class MediaS3Storage(S3Storage):
    location = 'media'
    object_parameters = {'CacheControl': 'public,max-age=604800,immutable'}
