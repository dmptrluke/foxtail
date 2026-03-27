import io
from unittest.mock import MagicMock

import pytest

from ..storages import LocalReadCache


def _mock_storage(content=b'fake image data'):
    """Build a mock storage whose open() returns a file-like with chunks()."""
    storage = MagicMock()
    file_obj = MagicMock()
    file_obj.chunks.return_value = [content]
    file_obj.__enter__ = lambda self: self
    file_obj.__exit__ = lambda self, *a: None
    storage.open.return_value = file_obj
    return storage


class TestLocalReadCache:
    # caches source on first read, serves from local cache on second
    def test_caches_read(self):
        storage = _mock_storage(b'image bytes')
        cache = LocalReadCache(storage)

        f1 = cache.open('photos/cat.jpg', 'rb')
        assert f1.read() == b'image bytes'
        f1.close()

        f2 = cache.open('photos/cat.jpg', 'rb')
        assert f2.read() == b'image bytes'
        f2.close()

        storage.open.assert_called_once()
        cache.cleanup()

    # write-mode open passes through to real storage
    def test_write_passthrough(self):
        storage = _mock_storage()
        cache = LocalReadCache(storage)

        cache.open('out.jpg', 'wb')

        storage.open.assert_called_once_with('out.jpg', 'wb')
        cache.cleanup()

    # save delegates to wrapped storage
    def test_save_passthrough(self):
        storage = _mock_storage()
        cache = LocalReadCache(storage)
        content = io.BytesIO(b'rendered')

        cache.save('rendition.jpg', content)

        storage.save.assert_called_once_with('rendition.jpg', content)
        cache.cleanup()

    # exists returns False when skip_exists is True
    def test_skip_exists(self):
        storage = _mock_storage()
        cache = LocalReadCache(storage, skip_exists=True)

        assert cache.exists('anything.jpg') is False
        storage.exists.assert_not_called()

    # exists delegates when skip_exists is False
    def test_exists_delegates(self):
        storage = _mock_storage()
        storage.exists.return_value = True
        cache = LocalReadCache(storage, skip_exists=False)

        assert cache.exists('photo.jpg') is True
        storage.exists.assert_called_once_with('photo.jpg')

    # cleanup removes cached temp files from disk
    def test_cleanup(self):
        storage = _mock_storage(b'data')
        cache = LocalReadCache(storage)

        f = cache.open('photo.jpg', 'rb')
        f.close()
        temp_path = cache._cache['photo.jpg']
        assert temp_path.exists()

        cache.cleanup()
        assert not temp_path.exists()
        assert cache._cache == {}

    # failed download does not leave a poisoned cache entry
    def test_failed_download_no_cache(self):
        storage = MagicMock()
        file_obj = MagicMock()
        file_obj.chunks.side_effect = ConnectionError('network timeout')
        file_obj.__enter__ = lambda self: self
        file_obj.__exit__ = lambda self, *a: None
        storage.open.return_value = file_obj

        cache = LocalReadCache(storage)

        with pytest.raises(ConnectionError):
            cache.open('photo.jpg', 'rb')

        assert 'photo.jpg' not in cache._cache
        cache.cleanup()

    # attributes not defined on proxy delegate to wrapped storage
    def test_getattr_delegation(self):
        storage = _mock_storage()
        storage.url.return_value = 'https://cdn.example.com/photo.jpg'
        cache = LocalReadCache(storage)

        assert cache.url('photo.jpg') == 'https://cdn.example.com/photo.jpg'
        storage.url.assert_called_once_with('photo.jpg')
