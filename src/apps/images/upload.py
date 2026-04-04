from pathlib import PurePosixPath

from django.utils.deconstruct import deconstructible

import shortuuid


@deconstructible
class scramble_upload:  # noqa: N801
    """Rename uploaded files to a random ID, preserving the extension."""

    def __init__(self, prefix):
        self.prefix = prefix

    def __call__(self, instance, filename):
        ext = PurePosixPath(filename).suffix.lower()
        return f'{self.prefix}/{shortuuid.uuid()}{ext}'
