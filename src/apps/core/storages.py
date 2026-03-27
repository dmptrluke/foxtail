from pathlib import Path
from tempfile import NamedTemporaryFile

from django.core.files import File as DjangoFile

from storages.backends.s3 import S3Storage


# noinspection PyAbstractClass
class MediaS3Storage(S3Storage):
    location = 'media'
    object_parameters = {'CacheControl': 'public,max-age=604800,immutable'}


class LocalReadCache:
    """Wrap a storage backend to cache reads locally. Writes pass through."""

    def __init__(self, storage, skip_exists=False):
        self._storage = storage
        self._skip_exists = skip_exists
        self._cache = {}

    def open(self, name, mode='rb'):
        if mode == 'rb':
            if name not in self._cache:
                tmp_path = Path(NamedTemporaryFile(delete=False, suffix=Path(name).suffix).name)  # noqa: SIM115
                try:
                    with self._storage.open(name, mode) as remote, tmp_path.open('wb') as tmp:
                        for chunk in remote.chunks():
                            tmp.write(chunk)
                except Exception:
                    tmp_path.unlink(missing_ok=True)
                    raise
                self._cache[name] = tmp_path
            return DjangoFile(self._cache[name].open(mode), name=str(self._cache[name]))
        return self._storage.open(name, mode)

    def exists(self, name):
        if self._skip_exists:
            return False
        return self._storage.exists(name)

    def cleanup(self):
        for path in self._cache.values():
            path.unlink(missing_ok=True)
        self._cache.clear()

    def __getattr__(self, attr):
        return getattr(self._storage, attr)
