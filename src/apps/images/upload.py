from pathlib import PurePosixPath
from uuid import uuid4


def scramble_upload(prefix):
    """Return an upload_to callable that renames files to a random UUID, preserving the extension."""

    def _upload_to(instance, filename):
        ext = PurePosixPath(filename).suffix.lower()
        return f'{prefix}/{uuid4().hex}{ext}'

    return _upload_to
