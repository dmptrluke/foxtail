from django.conf import settings
from django.core.exceptions import ValidationError

from markdownfield.validators import MARKDOWN_ATTRS, MARKDOWN_TAGS, Validator


class FileSizeValidator:
    def __init__(self, max_bytes=None):
        self.max_bytes = max_bytes

    def __call__(self, value):
        max_bytes = self.max_bytes if self.max_bytes is not None else settings.MAX_IMAGE_FILE_SIZE
        if value and hasattr(value, 'size') and value.size > max_bytes:
            mb = max_bytes / (1024 * 1024)
            raise ValidationError(f'File is too large. Maximum size is {mb:.0f} MB.')

    def __eq__(self, other):
        return isinstance(other, FileSizeValidator) and self.max_bytes == other.max_bytes

    def deconstruct(self):
        path = 'apps.core.validators.FileSizeValidator'
        args = ()
        kwargs = {}
        if self.max_bytes is not None:
            kwargs['max_bytes'] = self.max_bytes
        return path, args, kwargs


def file_size_validator(max_bytes=None):
    return FileSizeValidator(max_bytes=max_bytes)


VALIDATOR_EXTENDED = Validator(
    allowed_tags={
        *MARKDOWN_TAGS,
        'figure',
        'figcaption',
        'table',
        'thead',
        'tbody',
        'tr',
        'th',
        'td',
        'iframe',
    },
    allowed_attrs={
        **MARKDOWN_ATTRS,
        '*': {'id', 'class'},
        'a': {'href', 'alt', 'title', 'name'},
        'iframe': {'src', 'width', 'height', 'title', 'frameborder', 'allow', 'allowfullscreen', 'referrerpolicy'},
    },
)
