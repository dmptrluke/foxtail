from pathlib import PurePosixPath

import shortuuid


def scramble_upload(prefix):
    """Return an upload_to callable that renames files to a random ID, preserving the extension."""

    def _upload_to(instance, filename):
        ext = PurePosixPath(filename).suffix.lower()
        return f'{prefix}/{shortuuid.uuid()}{ext}'

    return _upload_to
